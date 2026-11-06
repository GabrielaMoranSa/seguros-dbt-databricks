"""Tests del generador. Los lanza pytest desde la raíz del repo; no necesitan Databricks ni la cartera real."""
import pytest

from generar_lotes import escribir_lote, inventar_todo, leer_argumentos, vida_poliza
from datetime import date

CARTERA_DE_PRUEBA = [{"IDpol": str(i), "VehPower": "6", "BonusMalus": "70"} for i in range(1, 301)]


@pytest.fixture
def historia():
    """Una fixture: prepara lo que varios tests necesitan. pytest la ejecuta una vez por cada test que la nombre y le da su resultado."""
    return inventar_todo(CARTERA_DE_PRUEBA, semilla=7)


def test_toda_poliza_empieza_por_su_alta(historia):
    polizas, _ = historia
    primeros = {}
    for mov in polizas:
        primeros.setdefault(mov["poliza_id"], mov["tipo"])
    assert set(primeros.values()) == {"ALTA"}


def test_cada_siniestro_cierra_con_la_reserva_a_cero(historia):
    _, siniestros = historia
    saldos = {}
    for mov in siniestros:
        saldos[mov["siniestro_id"]] = round(saldos.get(mov["siniestro_id"], 0) + mov["cambio_reserva"], 2)
    assert set(saldos.values()) == {0}


def test_el_mismo_lote_sale_igual_dos_veces(historia, tmp_path):
    polizas, siniestros = historia
    fecha = date(2026, 1, 15)
    escribir_lote(fecha, polizas, siniestros, tmp_path)
    primera = (tmp_path / f"mov_polizas_{fecha}.csv").read_bytes()
    escribir_lote(fecha, polizas, siniestros, tmp_path)
    assert (tmp_path / f"mov_polizas_{fecha}.csv").read_bytes() == primera


def test_otra_semilla_da_otra_historia():
    fila = {"IDpol": "1", "VehPower": "6", "BonusMalus": "70"}
    una = [vida_poliza(fila, semilla)[0][0]["prima_anual"] for semilla in (1, 2, 3)]
    assert len(set(una)) > 1


def test_los_dias_tienen_que_ser_uno_o_mas():
    # el test pasa si, dentro de este bloque, el programa se para
    with pytest.raises(SystemExit):
        leer_argumentos(["--desde", "2026-01-01", "--dias", "0"])
