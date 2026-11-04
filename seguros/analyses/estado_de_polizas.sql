-- numerar los movimientos de cada póliza, del más reciente al más antiguo
with movimientos_numerados as (
    select
        poliza_id,
        tipo,
        fecha_efecto,
        fecha_movimiento,
        row_number() over (partition by poliza_id order by fecha_efecto desc) as orden
    from workspace.raw.mov_polizas
)
select
    case when tipo = 'ANULACION' then 'Anulada' else 'Vigente' end as estado,
    count(*) as polizas
from movimientos_numerados
where orden = 1
group by estado