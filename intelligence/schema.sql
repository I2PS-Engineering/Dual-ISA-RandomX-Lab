-- ZTM Benchmark Intelligence schema (PostgreSQL).
-- Server-only: do not grant public direct table writes.
CREATE TABLE IF NOT EXISTS ztm_workers (
 worker_uuid uuid PRIMARY KEY,
 ztm_id varchar(5) NOT NULL UNIQUE
   CHECK (ztm_id ~ '^[A-Z2-9]{5}$'),
 registered_at timestamptz NOT NULL DEFAULT now(),
 last_seen timestamptz,
 consent_version text NOT NULL,
 revoked_at timestamptz
);
CREATE TABLE IF NOT EXISTS ztm_hardware (
 hardware_id uuid PRIMARY KEY,
 worker_uuid uuid NOT NULL REFERENCES ztm_workers(worker_uuid),
 fingerprint_sha256 char(64) NOT NULL,
 cpu_model text NOT NULL,
 cpu_vendor text,
 cpu_family text,
 cpu_stepping text,
 cpu_cores integer,
 cpu_threads integer,
 ram_bytes bigint,
 cache_json jsonb NOT NULL DEFAULT '{}'::jsonb,
 features_json jsonb NOT NULL DEFAULT '{}'::jsonb,
 environment_json jsonb NOT NULL DEFAULT '{}'::jsonb,
 captured_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS ztm_benchmark_runs (
 run_id uuid PRIMARY KEY,
 worker_uuid uuid NOT NULL REFERENCES ztm_workers(worker_uuid),
 hardware_id uuid NOT NULL REFERENCES ztm_hardware(hardware_id),
 ztm_version text NOT NULL,
 xmrig_version text,
 optimizer_version text,
 os_code text NOT NULL,
 arch_code text NOT NULL,
 started_at timestamptz NOT NULL,
 ended_at timestamptz,
 elapsed_seconds integer CHECK(elapsed_seconds >= 0),
 qualifying boolean NOT NULL DEFAULT false,
 completion_status text NOT NULL,
 raw_report jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS ztm_tested_profiles (
 profile_id uuid PRIMARY KEY,
 run_id uuid NOT NULL REFERENCES ztm_benchmark_runs(run_id),
 profile_label text NOT NULL,
 active_threads integer NOT NULL CHECK(active_threads > 0),
 init_threads integer,
 cpu_affinity jsonb,
 options_json jsonb NOT NULL DEFAULT '{}'::jsonb,
 mean_hs double precision,
 median_hs double precision,
 max_hs double precision,
 min_hs double precision,
 optimizer_score double precision,
 accepted_shares bigint,
 rejected_shares bigint,
 duration_seconds integer
);
CREATE TABLE IF NOT EXISTS ztm_measurements (
 measurement_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 profile_id uuid REFERENCES ztm_tested_profiles(profile_id),
 run_id uuid NOT NULL REFERENCES ztm_benchmark_runs(run_id),
 sampled_at timestamptz NOT NULL,
 hashrate_hs double precision,
 accepted_shares bigint,
 rejected_shares bigint,
 pool_difficulty double precision,
 temperature_c double precision,
 power_w double precision,
 metrics_json jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS ztm_measurements_run_time
  ON ztm_measurements(run_id, sampled_at);
CREATE TABLE IF NOT EXISTS ztm_winning_profiles (
 run_id uuid PRIMARY KEY REFERENCES ztm_benchmark_runs(run_id),
 profile_id uuid NOT NULL REFERENCES ztm_tested_profiles(profile_id),
 decided_at timestamptz NOT NULL DEFAULT now(),
 selection_method text NOT NULL,
 sustained_mean_hs double precision,
 sustained_median_hs double precision,
 observed_peak_hs double precision,
 accepted_shares bigint,
 rejected_shares bigint,
 verified boolean NOT NULL DEFAULT false
);
-- API authenticates workers, validates the request and writes using server-held credentials.
-- Use idempotent event IDs in the API layer; never trust a 5-character ZTM ID as a secret.
