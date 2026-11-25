# RetailRocket ETL implementation order

The warehouse grain for `fact_events` is **one source event row**.  The fact
pipeline can therefore run only after all four referenced dimensions exist.

| Order | Pipeline | Source | Target | Main rules |
| --- | --- | --- | --- | --- |
| 1 | `load_dim_category.hpl` | `category_tree.csv` | `dim_category` | Convert IDs to integers; map a blank `parentid` to `NULL`; upsert by `category_id`. |
| 2 | `load_dim_date.hpl` | distinct dates derived from `events.csv` | `dim_date` | Convert epoch milliseconds to dates; generate `date_key` (`YYYYMMDD`) and day/month/quarter/year attributes; upsert by `full_date`. |
| 3 | `load_dim_event_type.hpl` | distinct `event` values in `events.csv` | `dim_event_type` | Trim and validate event names; upsert by `event_type`. |
| 4 | `stage_item_latest_category.hpl` | `item_properties_part1.csv`, `item_properties_part2.csv` | staging stream/file | Keep only `property = categoryid`; cast timestamps; retain the newest category record per `itemid`; reject invalid category IDs. |
| 5 | `load_dim_item.hpl` | staged latest item categories | `dim_item` | Load one row per `item_id`; look up/validate its `category_id`; upsert by `item_id`.  Items with no category source record should still be loaded later from events with a NULL category. |
| 6 | `load_dim_visitor.hpl` | distinct `visitorid` values in `events.csv` | `dim_visitor` | Convert to bigint; remove duplicate visitor IDs; insert only new IDs. |
| 7 | `load_fact_events.hpl` | `events.csv` | `fact_events` | Type/validate rows; convert epoch milliseconds to `event_timestamp`; derive `date_key`; look up date, visitor, item and event-type surrogate keys; retain nullable `transaction_id`; write one fact row per source row. |
| 8 | `run_retailrocket_dw.hwf` | pipelines 1-7 | warehouse | Orchestrate the preceding pipelines, stop on error, and log read/written/rejected counts. |

## Execution constraints

- Pipelines 2, 3 and 6 have no dependency on one another, but implementing them after categories keeps the work easy to test.  Pipeline 5 requires 1 and 4; pipeline 7 requires 2, 3, 5 and 6.
- Each dimension load must be rerunnable: use its natural source key as the lookup key and only insert or update a changed attribute.  The existing category pipeline follows this pattern.
- `fact_events` currently has no source-row business key or unique constraint.  For an initial full load, run it once against an empty fact table.  Before making the workflow routinely rerunnable, add a stable `source_event_key` (or a documented event-row hash) with a unique constraint and use it for fact upserts/deduplication.  Do not use the current source `transactionid`: it is nullable and can occur in multiple rows.

## Fixed category pipeline

`load_dim_category.hpl` now uses `${PROJECT_HOME}/data/category_tree.csv` rather
than `${RETAILROCKET_DATA}/category_tree.csv`.  `PROJECT_HOME` is set by Hop when
the `RetailRocket_DWH` project is selected; the custom variable was not being
injected by the active runtime.  The source contains 1,669 unique categories and
25 root categories with a blank parent ID.
