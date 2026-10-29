-- Dimensión de pólizas: una fila por póliza (cartera + pólizas que solo aparecen en siniestros)
with cartera as (
    select
        poliza_id,
        edad_conductor,
        coeficiente_bonus_malus,
        antiguedad_vehiculo,
        area,
        region as codigo_region,
        {{ dbt_utils.generate_surrogate_key(['marca_vehiculo', 'combustible_vehiculo', 'potencia_vehiculo']) }} as vehiculo_key
    from {{ ref('stg_polizas') }}
),
faltantes as (
    select distinct
        s.poliza_id,
        cast(null as bigint)  as edad_conductor,
        cast(null as bigint)  as coeficiente_bonus_malus,
        cast(null as bigint)  as antiguedad_vehiculo,
        cast(null as string)  as area,
        'RSinPoliza'          as codigo_region,
        cast(null as string)  as vehiculo_key
    from {{ ref('stg_siniestros') }} as s
    left join {{ ref('stg_polizas') }} as p
        on s.poliza_id = p.poliza_id
    where p.poliza_id is null
)

select * from cartera
union all
select * from faltantes