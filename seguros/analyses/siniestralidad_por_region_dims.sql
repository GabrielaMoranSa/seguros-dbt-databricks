WITH cartera AS (
    SELECT
        d.codigo_region              AS region,
        Count(p.poliza_id)          AS polizas,
        SUM(p.exposicion_anios)          AS exposicion,
        SUM(p.n_siniestros)          AS siniestros_claimnb
    from workspace.dbt_gaby.stg_polizas p
    LEFT JOIN workspace.dbt_gaby.dim_poliza d 
    ON p.poliza_id = d.poliza_id
    GROUP BY codigo_region ),
siniestros AS (
    SELECT
      d.codigo_region              AS region,
      Count(s.poliza_id)          AS siniestros_sev,
      SUM(s.importe_siniestro)     AS claim_amount
    FROM workspace.dbt_gaby.stg_siniestros s
    LEFT JOIN workspace.dbt_gaby.dim_poliza d
    ON s.poliza_id=d.poliza_id
    GROUP BY d.codigo_region     
    )
  SELECT
  r.codigo_region,
  r.nombre_region,
  c.polizas, 
  c.siniestros_claimnb/c.exposicion AS frecuencia,
  s.claim_amount/s.siniestros_sev AS coste_medio,
  s.siniestros_sev,
  c.exposicion,
  c.siniestros_claimnb,
  s.claim_amount
FROM workspace.dbt_gaby.dim_region AS r
LEFT JOIN siniestros s
    ON r.codigo_region = s.region
LEFT JOIN cartera c
    ON r.codigo_region = c.region
