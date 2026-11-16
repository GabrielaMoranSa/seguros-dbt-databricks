with movimientos_numerados as (
    select
        poliza_id,
        prima_anual,
        tipo_movimiento as tipo,
        fecha_efecto,
        fecha_movimiento,
        row_number() over (partition by poliza_id order by fecha_efecto desc, movimiento_id desc) as orden
    from {{ ref('stg_mov_polizas') }})
select
    poliza_id,
    prima_anual,
    case when tipo = 'ANULACION' then 'Anulada' else 'Vigente' end as estado,
    fecha_efecto,
    cast(fecha_movimiento as TIMESTAMP) as fecha_registro
 from movimientos_numerados 
where orden = 1;