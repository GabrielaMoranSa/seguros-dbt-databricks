-- Dimensión de fechas: se genera, no se deriva. Un día por fila 

with dias as ( 
    {{ dbt_utils.date_spine( 
        datepart="day", 
        start_date="cast('2026-01-01' as date)", 
        end_date="cast('2028-01-01' as date)" 
    ) }} 
) 
select 
    cast(date_day as date)        as fecha, 
    year(date_day)                as anio, 
    quarter(date_day)             as trimestre, 
    month(date_day)               as mes, 
    day(date_day)                 as dia 
from dias 