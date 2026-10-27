# ADR-001: El grano de los hechos

## Fecha y estado
Fehca 26/10/2026, la decisión es una propuesta

## Contexto
Hay 2 tablas la de cartera y de siniestros, en la de cartera una fila representa una póliza y en la de siniestros una fila representa un siniestro.
Hay 195 siniestros que no tienen pólizas de las cuales para no descuadrar por el momento se propone agregarlo en una fila y colocarle región desconocida para dim_region, esos siniestros siguen sin póliza.
Hay siniestros sin importe, al contar la cantidad de siniestros de la tabla de cartera da una cantidad mayor que al contar los siniestros de la tabla de siniestros.
Para medir la frecuencia se tomo en cuenta los 36,102 reclamos que se contaron en la tabla de cartera ya que es el total de siniestros ocurridos considerando que algunos no se les ha pagado el importe.

## Opciones
- Esta la opción A, son dos tablas de hecho, cada una a su grano, la cartera por póliza y de siniestros por siniestro.
- Esta tambien la opción B de unir pólizas y siniestros fila a fila pero esto haría que por ejemplo el caso de las regiones sumaran doble o multiples veces.


## Decisión
Elijo la opcion A de dos tablas de hecho con cada una a su grano.
Para la frecuencia elegí que el total de siniestros que cuento en la tabla de cartera es el numero correcto considerando que es el total de siniestros ocurridos, sin embargo para el coste medio se toma en cuenta la cantidad de siniestros que cuento en la tabla de siniestros para considerar unicamente aquellos de los cuales ya se ha pagado importe.


## Consecuencias
Lo que gano con la opción A es que cuadra con la informacion del source y por ende no tengo incovenientes futuros por estar quitando algo que puede afectar descuadres con contabilidad.
Lo que debe recordar quien use las tablas que hay 195 siniestros sin polizas que suman 788K y que si forman parte del dato total del importe.