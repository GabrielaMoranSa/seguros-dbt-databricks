select
id_taller as codigo_taller,
nombre as nombre_taller,
provincia as provincia
FROM {{ref('talleres')}}