# Loader — freMTPL2

## What it does
`scripts/cargar_fremtpl2.py` checks the two freMTPL2 files in `data/` (policies and claims) before they are loaded into Databricks, and writes what it found to a log.

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
