SELECT
cast(movimiento_id as string) AS movimiento_id,
cast(siniestro_id as string) AS siniestro_id,
cast(poliza_id as bigint)  AS poliza_id,
tipo AS tipo_movimiento,
cast(fecha_ocurrencia as DATE) AS fecha_ocurrencia,
cast(fecha_declaracion as DATE) AS fecha_declaracion,
cast(fecha_movimiento as DATE) AS fecha_movimiento,
cast(cambio_reserva as DECIMAL(12,2)) as cambio_reserva,
cast(pago as DECIMAL(12,2)) as pago
from {{ source('raw', 'mov_siniestros') }}