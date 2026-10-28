-- Staging de pólizas: renombra a snake_case y fija tipos explícitos
select
    cast(IDpol as bigint)         as poliza_id,
    cast(ClaimNb as int)          as n_siniestros,
    cast(Exposure as double)      as exposicion_anios,
    Area                          as area,
    cast(VehPower as bigint)      as potencia_vehiculo,
    cast(VehAge as bigint)        as antiguedad_vehiculo,
    cast(DrivAge as bigint)       as edad_conductor,
    cast(BonusMalus as bigint)    as coeficiente_bonus_malus,
    VehBrand                      as marca_vehiculo,
    replace(VehGas, chr(39), '')   as combustible_vehiculo,
    cast(Density as bigint)       as densidad_zona,
    Region                        as region
from {{ source('raw', 'fremtpl2_freq') }}