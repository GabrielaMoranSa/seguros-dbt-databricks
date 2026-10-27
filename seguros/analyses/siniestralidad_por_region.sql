WITH cartera AS (
    SELECT
        Region                AS region,
        Count(IDpol)          AS polizas,
        SUM(Exposure)          AS exposicion,
        SUM(ClaimNb)          AS siniestros_claimnb
    FROM workspace.raw.fremtpl2_freq
    GROUP BY Region
),
siniestros AS (
    SELECT
      coalesce(f.Region, '(sin póliza)') AS region,
      Count(s.IDpol)          AS siniestros_sev,
      SUM(s.ClaimAmount)     AS claim_amount
    FROM workspace.raw.fremtpl2_sev s
    LEFT JOIN workspace.raw.fremtpl2_freq f
    ON f.IDpol=s.IDpol
    GROUP BY coalesce(f.Region, '(sin póliza)')
)
  SELECT
  s.region,
  c.polizas, 
  c.siniestros_claimnb/c.exposicion AS frecuencia,
  s.claim_amount/s.siniestros_sev AS coste_medio,
  s.siniestros_sev,
  c.exposicion,
  c.siniestros_claimnb,
  s.claim_amount
FROM siniestros s
LEFT JOIN cartera c
ON s.region=c.region