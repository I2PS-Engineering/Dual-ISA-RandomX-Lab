-- Apply intelligence/schema.sql first. Keep database inaccessible to public clients.
CREATE TABLE IF NOT EXISTS ztm_worker_credentials (
 worker_uuid uuid PRIMARY KEY REFERENCES ztm_workers(worker_uuid) ON DELETE CASCADE,
 token_hash char(64) NOT NULL UNIQUE,
 revoked_at timestamptz
);
CREATE TABLE IF NOT EXISTS ztm_ingested_events (
 worker_uuid uuid NOT NULL REFERENCES ztm_workers(worker_uuid),
 event_id text NOT NULL,
 received_at timestamptz NOT NULL DEFAULT now(),
 report jsonb NOT NULL,
 verified boolean NOT NULL DEFAULT false,
 PRIMARY KEY(worker_uuid,event_id)
);
CREATE INDEX IF NOT EXISTS ztm_ingested_events_received ON ztm_ingested_events(received_at);
