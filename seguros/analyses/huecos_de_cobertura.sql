-- Huecos de cobertura: una fila por hueco (anulación a rehabilitación) y los siniestros que cayeron dentro
with movimientos as (
    select
        movimiento_id,
        poliza_id,
        tipo_movimiento,
        lag(tipo_movimiento) over (partition by poliza_id order by fecha_efecto) as tipo_anterior,
        lag(fecha_efecto)    over (partition by poliza_id order by fecha_efecto) as fecha_anterior,
        fecha_movimiento,
        fecha_efecto,
        prima_anual
    from workspace.dbt_gaby.stg_mov_polizas
    where tipo_movimiento in ('ALTA', 'ANULACION', 'REHABILITACION')
),
huecos as (
    select
        poliza_id,
        fecha_anterior as desde,
        fecha_efecto   as hasta,
        datediff(fecha_efecto, fecha_anterior) as dias_sin_cobertura
    from movimientos
    where tipo_movimiento = 'REHABILITACION'
      and tipo_anterior = 'ANULACION'
),
siniestros as (
    select distinct
        siniestro_id,
        poliza_id,
        fecha_ocurrencia
    from workspace.dbt_gaby.stg_mov_siniestros
)
select
    h.poliza_id,
    h.desde,
    h.hasta,
    h.dias_sin_cobertura,
    count(s.siniestro_id) as siniestros_dentro
from huecos h
left join siniestros s
    on h.poliza_id = s.poliza_id
   and s.fecha_ocurrencia between h.desde and h.hasta
group by h.poliza_id, h.desde, h.hasta, h.dias_sin_cobertura