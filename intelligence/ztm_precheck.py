"""Non-blocking ZTM connectivity checks and automatic GUI scale planning.

Call probe_async from GUI threads; callback must be marshalled to
Tk's event loop via root.after. No mining or benchmark state is modified.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import socket
import ssl
from urllib.parse import urlsplit

_EXECUTOR = ThreadPoolExecutor(max_workers=3, thread_name_prefix="ztm-precheck")


@dataclass(frozen=True)
class Status:
    state: str
    detail: str


def check_internet(host="1.1.1.1", port=443, timeout=3):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return Status("online", "TCP reachability confirmed")
    except OSError as exc:
        return Status("offline", type(exc).__name__)


def check_https_source(url, timeout=3):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        return Status("unavailable", "Official HTTPS URL required")
    try:
        with socket.create_connection((parsed.hostname, parsed.port or 443), timeout=timeout) as raw:
            context = ssl.create_default_context()
            with context.wrap_socket(raw, server_hostname=parsed.hostname):
                return Status("online", "TLS connection established")
    except (OSError, ssl.SSLError) as exc:
        return Status("offline", type(exc).__name__)


def check_pool_tcp(host, port, timeout=3):
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return Status("online", "TCP reachable; Stratum handshake NOT verified")
    except (OSError, ValueError) as exc:
        return Status("offline", type(exc).__name__)


def probe_async(source_url, pool_host, pool_port, callback):
    jobs = {
        "network": _EXECUTOR.submit(check_internet),
        "xmrig_source": _EXECUTOR.submit(check_https_source, source_url),
        "pool_tcp": _EXECUTOR.submit(check_pool_tcp, pool_host, pool_port),
    }
    for name, job in jobs.items():
        job.add_done_callback(lambda future, key=name: callback(key, future.result()))
    return jobs


def suggested_zoom(screen_width, screen_height, pixels_per_inch=None):
    """Return an application font scaling preference, not the OS DPI multiplier.

    Calibrated conservatively for laptop readability. Tk native DPI scaling
    and desktop fractional scaling must still be accounted for by the GUI.
    """
    if screen_width <= 0 or screen_height <= 0:
        return 1.0
    # Smaller screens need more legible controls, while limited available
    # workspace requires scrolling instead of allowing panels to overlap.
    if screen_width <= 1366 or screen_height <= 768:
        return 1.35
    if screen_width <= 1920:
        return 1.20
    return 1.10


def clamp_manual_multiplier(value):
    return min(2.0, max(0.75, round(float(value), 2)))


def effective_font_zoom(auto_zoom, manual_multiplier):
    return round(auto_zoom * clamp_manual_multiplier(manual_multiplier), 3)
