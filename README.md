# Motor Insurance Analytics with dbt and Databricks

## What this is
An analytics engineering project built on public motor third-party liability (MTPL) insurance data (policies and claims).
It transforms raw data into clean, tested tables that are ready for business users.
The goal is to answer two core insurance questions: how often claims happen (claim frequency)
and how much they cost (claim severity), by driver, vehicle and region characteristics.

## Stack
- Databricks: storage and SQL engine (where the data lives and queries run).
- dbt: builds and tests the data models (staging layer and beyond).
- Python: downloads the source data, also validates and loads in Databricks

## Data
- Dataset: freMTPL2, French motor third-party liability insurance, published on OpenML
  in two tables: `freMTPL2freq` (one row per policy) and `freMTPL2sev` (one row per claim).
- License: CC0 (public domain), as listed on OpenML. Original source: the CASdatasets R package.
- The CSV files are not stored in this repository because of their size. To reproduce the project, run `scripts/bajar_fremtpl2.py`.


## How to run
7 steps to run the project:
1. Install the dependencies: `pip install -r requirements.txt` from the repo root, in this step it's important the virtual environment active.
2. Download the data: `python scripts/bajar_fremtpl2.py` from the repo root.
3. Load the data into Databricks: `python scripts/cargar_fremtpl2.py` from the repo root, in this step it's important the 3 environment variables(DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH and DATABRICKS_TOKEN).
4. Run `dbt deps` from seguros/
5. Build and test the models: `dbt build` from seguros/
6. Check data freshness: `dbt source freshness` from seguros/
7. Test the loader rules: Run `python -m pytest -v` from the repo root.

Also it is important to add the configuration file ~/.dbt/profiles.yml, who lives outside to the repo

## Project layout

scripts/
Content: 3  Python scripts: bajar_fremtpl2.py (dowload), cargar_fremtpl2.py (the loader) and validaciones.py (the loader rules)

seguros/
The dbt project: models/(staging models and their tests), analyses/ (one-off queries), tests/, seeds/ and snapshots/

docs/
Content: loader.md, bus_matrix.md and adr/ (ADR-000 y ADR-001)

tests/
Content: test_validaciones.py (pytest tests of the loader rules)

## Data model
- The fact and theis grain: portfolio (one row by one policy) and claims (one row by one claim with an amount).

- The two link: [bus matrix](docs/bus_matrix.md) and [ADR-001](docs/adr/001-grano-de-los-hechos.md)


## Status


Already done: The loader, loader rules in validaciones.py, covered by 3 pytest tests, staging with tests and freshness, the bus matrix, dim_region, dim_vehiculo, dim_poliza, dim_fecha and ADR-001.

Planned:
Create the new data with tables with movements of claims and policies.