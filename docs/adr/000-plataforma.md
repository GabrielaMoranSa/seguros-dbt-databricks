# ADR-000: Plataforma del proyecto

Fecha: 15-oct-2026 · Estado: aceptada

## Contexto
- El proyecto de portafolio necesita una plataforma de datos para construir y testear modelos
  con dbt sobre datos de seguros (freMTPL2: pólizas y siniestros de responsabilidad civil de autos).
- Las ofertas de empleo de aseguradoras y bancos piden con frecuencia Python, Spark y Databricks.
- El proyecto anterior (Olist) usó Azure SQL + dbt-sqlserver, que no muestra experiencia
  con plataformas tipo lakehouse.
- Restricción: costo cero o mínimo, ya que es un proyecto personal de aprendizaje.

## Opciones
1. Seguir con Azure SQL + dbt-sqlserver: ya conocido, pero no es la plataforma que piden las ofertas.
2. Databricks Free Edition: sin costo, misma plataforma que usan las empresas
   (Unity Catalog, SQL warehouse, dbt-databricks), con límites de uso.
3. Databricks de pago por uso: sin límites de Free Edition, pero con costo; requiere tope
   de gasto y apagado automático (plan B definido en la guía).

## Decisión
- Se elige Databricks Free Edition (opción 2).
- Prueba realizada el 15-oct-2026, resultado VERDE:
  - `dbt debug`, `dbt run` y `dbt test` pasan desde la Mac contra Free Edition.
  - Datos cargados en `workspace.raw` y verificados: 678.013 pólizas y 26.639 siniestros
    (mismos conteos en Python y en Databricks).
  - `stg_polizas` creada en `workspace.dbt_gaby` con 2 tests en PASS.

## Consecuencias
Se gana:
- Costo cero.
- Experiencia con la misma plataforma que usan aseguradoras y bancos.
- El flujo de trabajo es el estándar del sector: dbt local (VS Code) + Databricks como motor.

Se limita:
- Solo cómputo serverless, con un SQL warehouse de tamaño 2X-Small.
- Cuota diaria de cómputo: si se supera, el warehouse se apaga hasta el día siguiente pero (los datos no se pierden).
- No se permite uso comercial.
- No se practica la parte de infraestructura (clústeres, conexión a un Data Lake de la empresa).
- El token de acceso vence a los 90 días: renovar antes de mediados de enero de 2027.
