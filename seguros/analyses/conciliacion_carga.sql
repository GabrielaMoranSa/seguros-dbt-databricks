SELECT
'fremtpl2_freq' AS tabla,
COUNT(*) AS Total_filas,
COUNT(DISTINCT IDpol) AS Polizas_distintas,
COUNT_IF(IDpol IS NULL) AS Sin_IDPol,
ROUND(SUM(Exposure),2) AS Suma_control,
COUNT(DISTINCT `_loaded_at`) AS hora_distinta,
MAX(`_loaded_at`) AS maximo
FROM workspace.raw.fremtpl2_freq
UNION ALL
SELECT
'fremtpl2_sev' AS tabla,
COUNT(*) AS Total_filas,
COUNT(DISTINCT IDpol) AS Polizas_distintas,
COUNT_IF(IDpol IS NULL) AS Sin_IDPol,
ROUND(SUM(ClaimAmount),2) AS Suma_control,
COUNT(DISTINCT `_loaded_at`) AS hora_distinta,
MAX(`_loaded_at`) AS maximo
FROM workspace.raw.fremtpl2_sev