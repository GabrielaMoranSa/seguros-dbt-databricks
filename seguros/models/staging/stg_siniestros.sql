-- Staging de siniestros
with siniestros AS(select
    ROW_NUMBER() over (partition by IDpol order by ClaimAmount) as numero_siniestro,
    cast(IDpol as bigint)         as poliza_id,
    cast(ClaimAmount as DECIMAL(12,2))          as importe_siniestro
from {{ source('raw', 'fremtpl2_sev') }}    
)
select
    concat(cast(poliza_id as string), '-', cast(numero_siniestro as string)) as siniestro_id,
    poliza_id,
    numero_siniestro,
    importe_siniestro
from siniestros