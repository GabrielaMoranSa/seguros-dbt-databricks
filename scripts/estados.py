# scripts/estados.py
"""El estado de cada póliza a partir de sus movimientos."""


def ultimo_movimiento(movimientos):
    """movimientos: lista de diccionarios con poliza_id y tipo. Devuelve poliza_id -> último tipo."""
    ultimo = {}
    for m in movimientos:
        ultimo[m["poliza_id"]] = m["tipo"]
    return ultimo


def contar_estados(ultimo):
    conteo = {"Vigente": 0, "Anulada": 0}
    for tipo in ultimo.values():
        if tipo == "ANULACION":
            conteo["Anulada"] += 1
        else: 
            conteo["Vigente"] += 1
    return conteo


def estado_a_fecha(movimientos, fecha):
    """movimientos: lista de diccionarios con poliza_id, tipo y fecha_efecto (un date).
    Devuelve poliza_id -> tipo de su último movimiento con efecto hasta el día fecha,
    lo mismo que cuenta contar_estados."""
    hasta = [m for m in movimientos if m["fecha_efecto"] <= fecha]
    hasta.sort(key=lambda m: m["fecha_efecto"])
    return ultimo_movimiento(hasta)