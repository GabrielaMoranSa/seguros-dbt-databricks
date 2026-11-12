## CI

## What the CI checks:
The CI checks: pytest and dbt-build.
Pytest looks:
- all the test Python validation: test_validaciones(loader) and the test_generador
dbt_build looks:
- models
- dbt tests
all this things are building en dbt_ci

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