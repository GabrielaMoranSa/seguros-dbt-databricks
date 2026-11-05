
# Batch generator

## What it is
`scripts/generar_lotes.py` was written by my tutor, not by me. It is a tool
provided for this project. It creates synthetic data: the policy and claim movements are not real.


## What it makes
One batch per day. Each batch has two files:
- mov_polizas_YYYY-MM-DD.csv: one row per policy movement
- mov_siniestros_YYYY-MM-DD.csv: one row per claim movement (only on days with claims)

## How to run it
python scripts/generar_lotes.py --desde YYYY-MM-DD --dias N

- `--desde` (required): the first day you want to generate, it can be for the first time or to regenerate
- `--dias` (required): how many days
- `--semilla` (optional, default 2026): this is the number the randomness starts from, the same seed produces the same data
- `--salida` (optional, default data/lotes): is the folder where the batches are saved

If you run it twice with the same seed, it overwrites the files with the same name and the same content.

## How it gets into Databricks
`scripts/cargar_lotes.py` uploads the CSV files from data/lotes/ to Databricks and creates the tables mov_polizas and mov_siniestros in workspace.raw . It rebuilds the tables with
CREATE OR REPLACE, so it is idempotent, you can run it twice it doesn't matter, you get the same rows.
