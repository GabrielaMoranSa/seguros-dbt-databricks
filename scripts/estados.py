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