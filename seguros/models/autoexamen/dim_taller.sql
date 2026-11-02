SELECT
codigo_taller,
nombre_taller,
provincia
from {{ ref('stg_talleres') }}
UNION ALL
SELECT 'SIN_TALLER' AS codigo_taller,
'Sin taller' AS nombre_taller,
'Sin taller' AS provincia
