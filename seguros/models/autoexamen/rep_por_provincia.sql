SELECT
coalesce(d.provincia, 'Sin taller') as provincia,
COUNT(r.reparacion_id) as reparaciones,
SUM(r.importe) as importe,
SUM(r.importe) /COUNT(r.reparacion_id) as coste_medio
FROM {{ref('stg_reparaciones')}} r
LEFT JOIN {{ref('dim_taller')}} d
ON d.codigo_taller = r.codigo_taller
GROUP BY coalesce(d.provincia, 'Sin taller')