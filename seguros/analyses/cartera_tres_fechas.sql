-- W6 D4 · Cartera a tres fechas (15-ene, 31-ene, 14-feb de 2026): vigentes y prima anual de las vigentes.
-- Versión corregida tras la comparación: la prima suma solo las vigentes (la del reloj sumaba también las anuladas).
with cortes as (
    select date '2026-01-15' as corte
    union all
    select date '2026-01-31' as corte
    union all
    select date '2026-02-14' as corte
),
ultimo_movimiento as (
    select
    c.corte,
    m.poliza_id,
    m.tipo_movimiento,
    m.prima_anual,
    row_number () over (partition by c.corte, m.poliza_id order by m.fecha_efecto desc, m.movimiento_id desc) as orden
    from cortes as c
    left join workspace.dbt_gaby.stg_mov_polizas as m
    on m.fecha_efecto <= c.corte
)
select
corte,
sum(case when tipo_movimiento = 'ANULACION' then 0 else 1 end) as vigentes,
sum(case when tipo_movimiento = 'ANULACION' then 0 else prima_anual end) as prima_vigentes
from ultimo_movimiento
where orden = 1
group by corte
order by corte