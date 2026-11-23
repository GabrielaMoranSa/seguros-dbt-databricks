-- Hecho de pagos: una fila por pago (los movimientos PAGO de stg_mov_siniestros). Incremental, con merge por movimiento_id.
{{ config(materialized='incremental', unique_key='movimiento_id') }}

with pagos as (
    select
        movimiento_id,
        siniestro_id,
        poliza_id,
        fecha_movimiento,
        pago
    from {{ ref('stg_mov_siniestros') }}
    where tipo_movimiento = 'PAGO'
)

select * from pagos
{% if is_incremental() %}
where fecha_movimiento >= (select coalesce(max(fecha_movimiento), cast('1900-01-01' as date)) from {{ this }})
{% endif %}
