-- I2PS ZTM free-tier Neon analytics views.
-- Client-submitted results remain explicitly UNVERIFIED unless independently approved.
CREATE OR REPLACE VIEW ztm_analytics_overview AS
SELECT (SELECT count(*)::int FROM ztm_workers WHERE revoked_at IS NULL) registered_workers,
       (SELECT count(*)::int FROM ztm_ingested_events) submitted_reports,
       (SELECT count(*)::int FROM ztm_ingested_events WHERE verified) verified_reports;

CREATE OR REPLACE VIEW ztm_analytics_cpu AS
SELECT coalesce(nullif(trim(report #>> '{hardware,cpu_model}'),''),'Unknown') cpu_model,
       count(*)::int submitted_runs,
       count(*) FILTER(WHERE verified)::int verified_runs,
       round(avg(CASE WHEN (report #>> '{winner,sustained_mean_hs}') ~ '^[0-9]+(\.[0-9]+)?$'
                 THEN (report #>> '{winner,sustained_mean_hs}')::numeric END),2) submitted_mean_hs
  FROM ztm_ingested_events GROUP BY 1;

CREATE OR REPLACE VIEW ztm_analytics_platform AS
SELECT coalesce(report #>> '{worker,os}','Unknown') os_name,
       coalesce(report #>> '{worker,architecture}','Unknown') architecture,
       count(*)::int submitted_runs
  FROM ztm_ingested_events GROUP BY 1,2;
