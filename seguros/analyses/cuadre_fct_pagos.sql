with en_fct as (
    select
    count(*) as filas_fct,
    sum(pago) as pagado_fct
    from workspace.dbt_gaby.fct_pagos
), en_mov_sin as (
    select 
    count(*) as filas_mov,
    sum(pago) as pagado_mov
    from workspace.dbt_gaby.stg_mov_siniestros
    WHERE tipo_movimiento = 'PAGO'
)
SELECT
filas_fct,
pagado_fct,
filas_mov,
pagado_mov,
filas_mov-filas_fct as diferencia_filas,
pagado_mov-pagado_fct as diferencia_pagos,
CASE WHEN filas_mov-filas_fct = 0 and pagado_mov-pagado_fct = 0 then 'cuadra' else 'no cuadra' end as cuadre
from en_mov_sin as m 
CROSS JOIN en_fct as f

