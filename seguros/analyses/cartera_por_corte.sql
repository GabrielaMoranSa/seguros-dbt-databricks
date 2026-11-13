with cortes as (
    select date '2026-01-10' as corte union all
    select date '2026-01-20' union all
    select date '2026-01-30'
),
ultimo as (
    select
        c.corte,
        m.poliza_id,
        m.tipo_movimiento,
        row_number() over (
            partition by c.corte, m.poliza_id
            order by m.fecha_efecto desc, m.movimiento_id desc
        ) as orden
    from cortes as c
    join workspace.dbt_gaby.stg_mov_polizas as m
        on m.fecha_efecto <= c.corte
)
select
    corte,
    sum(case when tipo_movimiento = 'ANULACION' then 0 else 1 end) as vigentes,
    sum(case when tipo_movimiento = 'ANULACION' then 1 else 0 end) as anuladas,
    count(*)                                                        as polizas
from ultimo
where orden = 1
group by corte
order by corte