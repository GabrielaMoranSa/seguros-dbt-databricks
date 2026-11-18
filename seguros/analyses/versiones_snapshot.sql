-- Versiones nuevas de la segunda foto y cuántas no cambian ni estado ni prima
with versiones as (
    select
        poliza_id,
        estado,
        prima_anual,
        dbt_valid_from,
        lag(estado) over (partition by poliza_id order by dbt_valid_from) as estado_anterior,
        lag(prima_anual) over (partition by poliza_id order by dbt_valid_from) as prima_anterior
    from workspace.dbt_gaby.snap_estado_poliza
)
select
    count(*) as versiones_nuevas,
    count_if(estado = estado_anterior and prima_anual = prima_anterior) as sin_cambio
from versiones
where estado_anterior is not null