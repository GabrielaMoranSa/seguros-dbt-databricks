SELECT DISTINCT
id_reparacion as reparacion_id,
upper(trim(id_taller)) as codigo_taller,
fecha_reparacion as fecha_reparacion,
cast(importe as DECIMAL(12,2)) as importe
FROM {{ref('reparaciones')}}