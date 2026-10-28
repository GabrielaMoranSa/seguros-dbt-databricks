-- Dimensión de vehículos: una fila por combinación de marca, combustible y potencia
select distinct
    {{ dbt_utils.generate_surrogate_key([ 'marca_vehiculo', 'combustible_vehiculo' , 'potencia_vehiculo' ]) }}  as vehiculo_key,
    marca_vehiculo               as marca_vehiculo,
    combustible_vehiculo         as combustible_vehiculo,
    potencia_vehiculo            as potencia_vehiculo
from {{ ref('stg_polizas') }}