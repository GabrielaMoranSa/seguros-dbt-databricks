SELECT
codigo_region,
nombre_region
FROM {{ref('regiones')}}
UNION ALL
SELECT 'RSinPoliza' AS codigo_region,
'Region_sin_poliza' AS nombre_region