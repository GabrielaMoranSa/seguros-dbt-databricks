WITH reparaciones as (
    SELECT
    SUM(importe) as total_importe
    FROM {{ref('stg_reparaciones')}}
),
provincias as (
    SELECT
    SUM(importe) as total_importe
    FROM {{ref('rep_por_provincia')}}
)
SELECT
r.total_importe as total_staging,
p.total_importe as total_informe
FROM reparaciones r, provincias p
WHERE r.total_importe <> p.total_importe
