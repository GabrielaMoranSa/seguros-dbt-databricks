# Loader — freMTPL2

## What it does
`scripts/cargar_fremtpl2.py` checks the two freMTPL2 files in `data/` (policies and claims) before they are loaded into Databricks, and writes what it found to a log.
 then load the files to the volumne, then do the tables fremtpl2_freq and fremtpl2_sev in workspace.raw using CREATE OR REPLACE, next step is add the column with the date and time, and finished, let the exit code and summary in logs/ultima_carga.json

## What it checks
- Structure (both files):the file exists, it has exactly the expected columns (12 for policies, 2 for claims) and it has rows. If this fails, nothing else is checked.
- Policies (`fremtpl2_freq.csv`): `IDpol` is never empty or duplicated, `ClaimNb` is never negative, `Exposure` is always greater than 0.
- Claims (`fremtpl2_sev.csv`): `IDpol` is never empty, `ClaimAmount` is always greater than 0. `IDpol` may repeat, because one policy can have several claims.

## What happens when a check fails
- A broken file stops the load: each problem is written as an `ERROR` line, with the file name and the number of rows affected.
- Unusual but valid data does not stop the load: it is written as a `WARNING` (for example, policies with `Exposure` over one year).
- Everything goes to `logs/loader.log` (all levels, kept across runs); the console only shows `INFO` and above.

## How to run it
From the repo root, with the virtual environment active:
`python scripts/cargar_fremtpl2.py`
The loader needs 3 environment variables: DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH and DATABRICKS_TOKEN


## What to check after a load

| Witness | Who runs or writes it, and when | What it says when the load fails |
|---|---|---|
| 1. Terminal | the data engineer launch the load during the process | lines with ERROR |               
| 2. `logs/loader.log` | Loader, during the process | files and rows with ERROR |
| 3. `logs/ultima_carga.json` | Loader, when finished the process | code 1, if the program failed in the middle, the JSON it will be the old file |
| 4. Exit code | The loader when exit the process  | Different to 0 |
| 5. `dbt source freshness` |  the next day: by the data engineer or a automatically task | WARN or ERROR |


Freshness is the only witness who notify if the loader it wasn't run because it doesn't depend on the loader.
