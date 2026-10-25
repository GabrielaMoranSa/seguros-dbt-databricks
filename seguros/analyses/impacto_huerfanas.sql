SELECT
    count(*) AS cantidad,
    COUNT(DISTINCT s.IDPol) AS polizas_distintas,
    round(SUM(s.claimAmount),2) AS total_siniestro,
    round(avg(s.claimAmount),2) AS importe_medio,
    round(sum(s.claimAmount) * 100 / sum(sum(s.claimAmount)) OVER (), 2) AS pct_siniestro,
    CASE WHEN f.IDpol IS NULL THEN 0 ELSE 1 END AS etiqueta
FROM workspace.raw.fremtpl2_sev AS s
LEFT JOIN workspace.raw.fremtpl2_freq AS f
    ON s.IDpol = f.IDpol
GROUP BY etiqueta