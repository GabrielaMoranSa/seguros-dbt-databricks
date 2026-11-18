# tests/test_estados.py
from datetime import date

from estados import ultimo_movimiento, contar_estados, estado_a_fecha


def test_se_queda_con_el_ultimo():
    movimientos = [
        {"poliza_id": 1, "tipo": "ALTA"},
        {"poliza_id": 2, "tipo": "ALTA"},
        {"poliza_id": 1, "tipo": "ANULACION"},
    ]
    assert ultimo_movimiento(movimientos) == {1: "ANULACION", 2: "ALTA"}


def test_cuenta_una_poliza_por_estado():
    ultimo = {1: "ANULACION", 2: "ALTA"}
    assert contar_estados(ultimo) == {"Vigente": 1, "Anulada": 1}


def test_poliza_anulada_y_rehabilitada():
    # Póliza que tiene ALTA, ANULACION y luego REHABILITACION
    movimientos = [
        {"poliza_id": 1, "tipo": "ALTA"},
        {"poliza_id": 1, "tipo": "ANULACION"},
        {"poliza_id": 1, "tipo": "REHABILITACION"},
    ]
    
    ultimo = ultimo_movimiento(movimientos)
    # Como la rehabilitación no es ANULACION, nuestra lógica lo cuenta como Vigente
    assert ultimo == {1: "REHABILITACION"}
    assert contar_estados(ultimo) == {"Vigente": 1, "Anulada": 0}

def test_el_orden_importa_en_el_historial():
    # Caso A: Termina en ANULACION
    movimientos_termina_anulada = [
        {"poliza_id": 1, "tipo": "ALTA"},
        {"poliza_id": 1, "tipo": "ANULACION"},
    ]
    assert ultimo_movimiento(movimientos_termina_anulada) == {1: "ANULACION"}

    # Caso B: El mismo contenido pero el orden se invierte y termina en ALTA
    movimientos_termina_alta = [
        {"poliza_id": 1, "tipo": "ANULACION"},
        {"poliza_id": 1, "tipo": "ALTA"},
    ]
    assert ultimo_movimiento(movimientos_termina_alta) == {1: "ALTA"}


def test_anulada_y_rehabilitada_segun_la_fecha():
    # Alta el 1-ene, anulada el 10-ene, rehabilitada el 20-ene
    movimientos = [
        {"poliza_id": 1, "tipo": "ALTA", "fecha_efecto": date(2026, 1, 1)},
        {"poliza_id": 1, "tipo": "ANULACION", "fecha_efecto": date(2026, 1, 10)},
        {"poliza_id": 1, "tipo": "REHABILITACION", "fecha_efecto": date(2026, 1, 20)},
    ]
    assert estado_a_fecha(movimientos, date(2026, 1, 15)) == {1: "ANULACION"}
    assert estado_a_fecha(movimientos, date(2026, 1, 25)) == {1: 'REHABILITACION'}


def test_alta_despues_de_la_fecha():
    # Alta el 20-ene, preguntada el 15-ene
    movimientos = [
        {"poliza_id": 1, "tipo": "ALTA", "fecha_efecto": date(2026, 1, 20)},
    ]
    assert estado_a_fecha(movimientos, date(2026, 1, 15)) == {}