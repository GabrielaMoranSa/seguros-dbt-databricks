# ADR-003: Que para un PR

## Fecha y estado
Fehca 13/11/2026, decisión esta aceptada

## Contexto
- El proyecto tiene 37 tests de dbt y 19 de pytest.
  - 34 tests de dbt paran el PR ante cualquier fallo (severidad error, la que viene por defecto, más el singular con `severity = 'error'`).
  - 3 tests tienen umbral: avisan si encuentran entre el más de 0 y el umbral, y paran si lo superan:
    - `relationships` de freq a sev (fuentes), umbral 9116
    - `relationships` de sev a freq (fuentes), umbral 195
    - `relationships` de stg_siniestros a stg_polizas (staging), umbral 195
- El miércoles puse un PR en rojo a propósito: quité REHABILITACION de los `accepted_values` de tipo_movimiento en stg_mov_polizas; el check dbt-build salió en rojo y el botón de merge quedó inhabilitado.
- El jueves, con el CI slim, en el PR corrieron 5 tests de los 37 del proyecto, porque el slim solo construyó lo que cambió y lo que depende de ello, y el resto lo lee de dbt_gaby. Ese día cambié el modelo stg_mov_polizas, y esos 5 tests eran los suyos.

## Opciones
- Opción A · Todo para. Si los 56 tests pararan ante cualquier fallo, hoy el PR pasará hasta que negocio corrija esos datos, porque ya existen 195 siniestros sin póliza y 9116 pólizas que declaran siniestros sin importe. Coste: se bloque el PR.
- Opción b · Lo conocido avisa con umbral, lo nuevo para. Los problemas que ya conocemos (195 y 9116) avisan en amarillo; si crecen, paran. Coste: pueden pasan sin problema en dado caso sea menor que 195 y 9116.
- Tiempo del CI (GitHub Actions, workflow dbt, ejecución completa): build entero entre 1 min 3 seg y 1 min 22 seg; slim entre 59s y 1 min 23 seg. El tiempo no decide entre A y B.

## Decisión
Elijo la opción B, ya que es la data que nos funciona por el momento tenemos y sino pararia el PR hasta que negocios logre apoyarnos con la data faltante, en este caso lo que se pretende si el dato baja ese umbral se vea corregido para que ir disminuyendo esa cantidad de 195 siniestros sin poliza y las 9116 pólizas que declaran siniestros sin importe

## Consecuencias
- Buena: los 3 warning no me afectan el PR y de alguna manera con el umbral se tiene controlado.
- Mala: si el número de huérfanos baja (por ejemplo, 45), el test pasa, y entonces podemos no darnos cuenta de dejar la puerta que lleguen otros 150 siniestros con el mismo problema, necesitamos bajar el umbral cuando pase.
- Quién lo paga: en este caso puedo pagarlo el consumidor en dado caso no me de cuenta y baje los siniestros sin poliza y lleguen otro nuevos
los informes traerían data diferente y el error pasara por el PR sin problema.

## Supuestos

- Supuesto: que los 195 siniestros sin póliza son siempre los mismos. Si negocio arreglara algunos y entraran otros tantos nuevos, el total seguiría en 195 y el test no lo detectaría.
- Supuesto: con este tamaño de proyecto, el tiempo del CI depende más del arranque que de lo que se construye; solo hay 2 ejecuciones slim para comprobarlo.
- Que un test con error para el PR lo comprueba: PR #3, ejecución dbt #3, log `Done. PASS=42 WARN=3 ERROR=1`.