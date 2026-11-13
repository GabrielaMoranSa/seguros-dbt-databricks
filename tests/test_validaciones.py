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


def test_freq_con_ClaimNb_negativo_se_para(tmp_path):
    ruta = tmp_path / "freq.csv"
    ruta.write_text(CABECERA_FREQ + "1,-2,0.5,D,5,0,55,50,B12,Regular,1217,R82\n")
    df, problemas = validar_freq(ruta)
    assert problemas == ["ClaimNb negativo en 1 filas"]

def test_freq_con_exposure_cero_se_para(tmp_path):
    ruta = tmp_path / "fre.csv"
    ruta.write_text(CABECERA_FREQ + "1,0,0,D,5,0,55,50,B12,Regular,1217,R82\n")
    df, problemas = validar_freq(ruta)
    assert problemas == ["Exposure menor o igual a 0 en 1 filas"]




def test_sev_con_importe_cero_se_para(tmp_path):
    # preparar: una fila con importe 0
    ruta = tmp_path / "sev.csv"
    ruta.write_text("IDpol,ClaimAmount\n1,0\n")
    # ejecutar
    df, problemas = validar_sev(ruta)
    # comprobar: mensaje de la línea 100, con n = 1
    assert problemas == ["ClaimAmount menor o igual a 0 en 1 filas"]


def test_sev_sin_una_columna_se_para(tmp_path):
    # preparar: falta la columna ClaimAmount
    ruta = tmp_path / "sev.csv"
    ruta.write_text("IDpol\n1\n")
    # ejecutar
    df, problemas = validar_sev(ruta)
    # comprobar: mensaje de la línea 31; sorted() devuelve una lista, por eso los corchetes
    assert problemas == ["faltan columnas: ['ClaimAmount']"]


def test_sev_sin_filas_se_para(tmp_path):
    # preparar: solo la cabecera, sin ninguna fila
    ruta = tmp_path / "sev.csv"
    ruta.write_text("IDpol,ClaimAmount\n")
    # ejecutar
    df, problemas = validar_sev(ruta)
    # comprobar: mensaje de la línea 35
    assert problemas == ["el archivo no tiene filas"]


def test_freq_con_una_columna_de_mas_se_para(tmp_path):
    ruta = tmp_path / "freq.csv"
    cabecera = CABECERA_FREQ.replace("\n", ",Extra\n")
    fila = POLIZA.format(id=1).replace("\n", ",x\n")
    ruta.write_text(cabecera + fila)
    df, problemas = validar_freq(ruta)
    assert problemas == ["sobran columnas: ['Extra']"]    

def test_sev_con_una_columna_de_mas_se_para(tmp_path):
    ruta = tmp_path / "sev.csv"
    ruta.write_text("IDpol,ClaimAmount,Extra\n1,100.0,x\n")
    df, problemas = validar_sev(ruta)
    assert problemas == ["sobran columnas: ['Extra']"]   
