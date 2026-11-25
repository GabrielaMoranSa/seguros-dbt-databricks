# ADR-004: Cómo guarda la historia el proyecto

## Fecha y estado
- Fecha: 25/11/2026, decisión aceptada

## Contexto
- Qué guarda hoy el proyecto (una línea por pieza):
  - Estado de hoy: int_estado poliza, y cada build la sobrescribe así que no guarda historia.
  - Movimientos: son la película, ya que los movimientos se acumulan no se borran 
  - Snapshot (desde el lunes): guarda como estaba la poliza es decir su estado, su prima, su fecha de efecto al momento de cada foto, y conserva las versiones anteriores cerradas con dbt_valid_to.
  - Hecho incremental (fct_pagos): unicamente se agrega los nuevos dias sin cargar completo todo.
- Segunda foto: 903 versiones, 25 sin cambio de estado ni de prima.
- Tercera foto, con la estrategia en yml check sobre estado, prima_anual y fecha_efecto: 486 versiones, 7 sin cambio.
- fct_pagos: primer build 134 pagos; segundo build entraron 51; el lote tarde traía 13; en el cuadre faltaron 13. El jueves la ventana paso a un gap de 2 días y el cuadre el mismo valor 198 = 198 ya que considero 2 dias antes del 14.

## Opciones
- Opción A, incremental con la ventana anterior. Número: 185, faltaron 13. Coste: cualquier archivo que llegue tarde ya no se toma en cuenta
- Opción B, incremental con la ventana de 2 días. Número: 198 = 198. Coste: que actualmente solo cubre dos días si un archivos llega con mas de 2 días de retardo ya no se carga


## El CI y los incrementales
- Qué vi el viernes en el log y en dbt_ci: que la versión 0 que vi con describe history tenía CREATE y todas las filas completas.
Versión 0: CREATE, 198 filas (build entero).
Versión 1: MERGE, 48 actualizadas, 0 insertadas.
El miércoles: dbt_ci tenía 198 filas y dbt_gaby 185. Eso significa que cuando corrio en el PR se construyó completo, es decir no pudo ver el problema de los 13 pagos.
Opciones: reconstruir en cada PR / dbt clone desde dbt_gaby / dejarlo como está sabiéndolo.
Elijo  dbt clone desde dbt_gaby porque es importante que tengo tanto en dbt_gaby como dbt_ci lo mismo, y conocer lo que esta ocurriendo para realizar las respectivas pruebas a los tests.

## Decisión
Para fct_pagos: elijo la opción B para dar un gap de dos días que llegue, porque con 2 días el cuadre dio 198 = 198.
Para el CI: dbt clone, porque es importante que tengo tanto en dbt_gaby como dbt_ci lo mismo, y conocer lo que esta ocurriendo para realizar las respectivas pruebas a los tests.
En el caso que no vio que me faltaban los 13 pagos me parece erroneo ya que el PR y todo hubiera estado bien pero yo en dbt_gaby no hubiera entendido que pasaba.


## Consecuencias
- Buena: Lo que gano con la ventana de dos días es que cualquier atraso de 1 o 2 días entrara la carga de ese lote, para el dbt_clone lo bueno es que tanto en dbt_gaby como dbt_ci estaria viendo lo mismo.
- Mala (qué se puede escapar): Para la ventana de dos días lo malo es que si algo pasa de una atraso de dos días no lo vería, y para el dbt clone lo malo es que una vez tenga problemas en dbt_gaby tendre el problema en dbt_ci, ningun test lo para y el cuadre es una analisis que alguien debe hacer manual.
- Quién lo paga: lo paga el consumidor de data para ambos si el archivo no trae la data completa porque paso y falto carga un día, la data la estara viendo incorrecta y le faltaran pagos, y con respecto a dbt clone si el CI hereda el hueco y el PR sale en verde fusionara sin problema y la data erronea llega hasta el consumidor.

## Supuestos
- Supuesto retraso: si supongo que ningún lote llega con más de 2 días de retraso. Solo lo vi con el lote del 12. Si llega uno con 3 días, no se cargara, por ende cuando corra la query no cuadrara y peligrosamente pasara en silencio sino me doy cuenta.
- Supuesto de la foto: si la foto se saca cada día. Esta semana la saqué 3 veces. Si una póliza cambia dos veces entre dos fotos, el snapshot no vera el cambio porque lo leera como que no hubo cambio en la versión.