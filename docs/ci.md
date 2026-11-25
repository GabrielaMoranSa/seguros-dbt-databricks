## CI

## What the CI checks:
The CI checks: pytest and dbt-build. (dbt-build only build the models and dependences had changed it, it's not for all the project. To the orher parts it takes
borrow of dbt_gaby )
Pytest looks:
- all the test Python validation: test_validaciones(loader) and the test_generador
dbt_build looks:
- models
- dbt tests

## Incremental models
- fct_pagos, currently is the ones incremental models, using a unique key with movimiento_id.
- After the first run (complete), every run only merge de new rows, and re-reads the last two days.
- The filter starts two days before the latest movement date already in the table.
- fct_pagos is new and before today never had load in Databricks in the schema dbt_ci. Today run complete the table and after today run the merge 
- Wednesday of CI is green with 198 rows but in my Mac have 185 rows. No test compares fct_pagos with staging.

## What blocks a pull request: 

- Have 6 test:
- The first is to look if 9.116 you can’t over the number it warns
- Second and third is to look if 195 you can’t over the number (raw and staging)
- Four and five, its to respect a list for the columna tipo_movimiento with the configuration accepted_values (this is for claims and policies)
- The last one, its to compare the total amount of 195 which is 788.714,18, one of then you can’t over the number

## How to run the same checks locally: 

With two commands:
 python -m pytest -v inside the raiz and dbt build inside seguros/.

## Where the credentials live: 

The three secrets lives in GitHub secrets:
DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH y DATABRICKS_TOKEN