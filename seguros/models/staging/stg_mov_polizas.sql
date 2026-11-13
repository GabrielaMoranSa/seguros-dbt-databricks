SELECT
cast(movimiento_id as string) AS movimiento_id,
cast(poliza_id as bigint)  AS poliza_id,
tipo AS tipo_movimiento,
cast(fecha_movimiento as DATE) AS fecha_movimiento,
cast(fecha_efecto as DATE) AS fecha_efecto,
datediff(cast(fecha_movimiento as DATE), cast(fecha_efecto as DATE)) AS dias_hasta_registro,
cast(prima_anual as DECIMAL(12,2)) as prima_anual
from {{ source('raw', 'mov_polizas') }}