
--1. Movimientos con poliza_id vacío
SELECT
poliza_id
from workspace.dbt_gaby.stg_mov_polizas
WHERE poliza_id is NULL;

-- 2. Busca movimientos de stg_mov_polizas cuya póliza no existe en stg_polizas
SELECT
p.poliza_id,
m.poliza_id
from workspace.dbt_gaby.stg_mov_polizas as m
left join workspace.dbt_gaby.stg_polizas as p
ON m.poliza_id = p.poliza_id
WHERE p.poliza_id is NULL;