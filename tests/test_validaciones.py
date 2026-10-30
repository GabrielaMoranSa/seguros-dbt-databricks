"""Tests de las reglas del loader. Cada test escribe un CSV pequeño en una carpeta temporal y comprueba
qué problemas encuentra el validador. No tocan data/."""
from validaciones import validar_freq, validar_sev

CABECERA_FREQ = "IDpol,ClaimNb,Exposure,Area,VehPower,VehAge,DrivAge,BonusMalus,VehBrand,VehGas,Density,Region\n"
POLIZA = "{id},0,0.5,D,5,0,55,50,B12,Regular,1217,R82\n"


def test_freq_correcto_no_tiene_problemas(tmp_path):
    ruta = tmp_path / "freq.csv"
    ruta.write_text(CABECERA_FREQ + POLIZA.format(id=1) + POLIZA.format(id=2))
    df, problemas = validar_freq(ruta)
    assert problemas == []
    assert len(df) == 2


def test_freq_con_idpol_repetido_se_para(tmp_path):
    ruta = tmp_path / "freq.csv"
    ruta.write_text(CABECERA_FREQ + POLIZA.format(id=1) + POLIZA.format(id=1))
    df, problemas = validar_freq(ruta)
    assert problemas == ["IDpol repetido en 1 filas"]


def test_sev_sin_idpol_se_para(tmp_path):
    ruta = tmp_path / "sev.csv"
    ruta.write_text("IDpol,ClaimAmount\n1,100.0\n,250.0\n")
    df, problemas = validar_sev(ruta)
    assert problemas == ["IDpol vacío en 1 filas"]
