# ADR-002: Carga de lotes

## Fecha y estado
Fehca 08/11/2026, la decisión es una propuesta

## Contexto
Hoy cargar_lotes.py sube todos los archivos de data/lotes/ y reescribe la tabla entera con CREATE OR REPLACE. Con 30 días de lotes son 30 archivos y 31,175 filas (pólizas) y 21 archivos y 197 filas (siniestros). La última carga (4/11/2026) empezó a las 22:12:10 y terminó a las 22:13:16 unos 66 segundos. Cada noche llega un lote nuevo, así que la duda es qué pasará con un año de lotes, y si convendría añadir solo el lote de cada noche en vez de reconstruir todo.


## Opciones
Opción A, recostruir todo, es lo que hace hoy cada vez que se corre se suben todos los archivos y CREATE OR REPLACE cada noche. Ahora mismo lo que tarde la opción son 66 segundos con 30 días, la estimación para un año sería 12 veces mas que el tiempo medido es decir 792 segundos suponiendo que crece con el número de archivos.

Opción B, añadir solo el lote de la noche, subir solo el archivo nuevo insertando solos sus filas nuevas. Para esta opción si actualmente se tarda 66 segundos los 30 días sería una estimación de 2.2 segundos por cada día por lote.


## Decisión

Elijo la opción A, que me permite estar segura que cada carga estará completa ya que igual manera el reconstuir cada dia me permite tener los mismos resultados sin duplicados porque tiene la caracteristica que es idempotente. Ademas 13 minutos por la carga de un año en una noche me parece razonable.

## Consecuencias

La consecuencia principal de esta decisión es que el tiempo de carga crece cada noche de 66s que tengo hoy hasta una estimacion de los 792 segundos(12 veces mas que lo actual tengo) que tendre en un año, lo que tendría que ser pagado en tiempo por el consumidor un analista de datos del area de reclamos esperando a ver la data al dia de ayer y lo que paga en dinero la compañia es mayor capacidad de basos de datos al reconstruir cada noche.

## Supuestos

- Supuesto 1: los 792 segundos solo si los archivos crecieran en la misma proporcion de como fueran calculos los 66 segundos que actualmente se tiene.
- Supuesto 2: no sé cuánto aumenta el coste de almacenamiento guardar las versiones (lo que se es que sí se guardan: comprobado con `describe history workspace.raw.mov_polizas`).