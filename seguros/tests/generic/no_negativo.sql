-- Test genérico propio: falla con cada fila en la que la columna es menor que cero.
{% test no_negativo(model, column_name) %}
select *
from {{ model }}
where {{ column_name }} < 0
{% endtest %}
