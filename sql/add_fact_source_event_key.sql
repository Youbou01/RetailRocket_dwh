-- Enables safe retries of load_fact_events for the unchanged events.csv file.
-- source_event_key is the CSV data-row ordinal (not transactionid).
-- Run this against the same database used by retailrocket_dw_conn before loading facts.
-- Existing fact rows without keys are not guessed or rewritten: the migration
-- stops and rolls back if it finds any, so they must be reconciled first.

BEGIN;

ALTER TABLE public.fact_events
  ADD COLUMN IF NOT EXISTS source_event_key BIGINT;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM public.fact_events
    WHERE source_event_key IS NULL
  ) THEN
    RAISE EXCEPTION
      'fact_events contains rows without source_event_key; reconcile/backfill them before applying this migration';
  END IF;
END;
$$;

ALTER TABLE public.fact_events
  ALTER COLUMN source_event_key SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conrelid = 'public.fact_events'::regclass
      AND conname = 'uq_fact_events_source_event_key'
  ) THEN
    ALTER TABLE public.fact_events
      ADD CONSTRAINT uq_fact_events_source_event_key UNIQUE (source_event_key);
  END IF;
END;
$$;

COMMIT;
