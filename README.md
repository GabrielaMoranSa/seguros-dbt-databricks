# Motor Insurance Analytics with dbt and Databricks

## What this is
An analytics engineering project built on public motor third-party liability (MTPL) insurance data (policies and claims).
It transforms raw data into clean, tested tables that are ready for business users.
The goal is to answer two core insurance questions: how often claims happen (claim frequency)
and how much they cost (claim severity), by driver, vehicle and region characteristics.

## Stack
- Databricks: storage and SQL engine (where the data lives and queries run).
- dbt: builds and tests the data models (staging layer and beyond).
- Python: downloads the source data.

## Data
- Dataset: freMTPL2, French motor third-party liability insurance, published on OpenML
  in two tables: `freMTPL2freq` (one row per policy) and `freMTPL2sev` (one row per claim).
- License: CC0 (public domain), as listed on OpenML. Original source: the CASdatasets R package.
- The CSV files are not stored in this repository because of their size and their own license.
  To reproduce the project, run `scripts/bajar_fremtpl2.py`.