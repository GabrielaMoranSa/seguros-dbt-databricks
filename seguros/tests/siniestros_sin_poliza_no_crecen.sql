-- Test singular: falla si los siniestros sin póliza crecen en cantidad o en importe
with sin_poliza as (
    select
        s.siniestro_id,
        s.importe_siniestro
    from {{ ref('stg_siniestros') }} as s
    left join {{ ref('stg_polizas') }} as p
        on s.poliza_id = p.poliza_id
    where p.poliza_id is null
)
select
    count(*)                          as siniestros_sin_poliza,
    round(sum(importe_siniestro), 2)  as importe_sin_poliza
from sin_poliza
having count(*) > 195
    or sum(importe_siniestro) > 788714.18