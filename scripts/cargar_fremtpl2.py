import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from databricks import sql

log = logging.getLogger("loader")


def configurar_logging():
    """Dos destinos: consola (INFO o más) y archivo logs/loader.log (DEBUG o más)."""
    Path("logs").mkdir(exist_ok=True)
    consola = logging.StreamHandler()
    consola.setLevel(logging.INFO)
    # Decisión B2: el log se ACUMULA entre ejecuciones (mode="a"). Así queda el
    # historial de cada carga; con mode="w" una segunda corrida borraría la de la noche.
    archivo = logging.FileHandler("logs/loader.log", mode="a", encoding="utf-8")
    archivo.setLevel(logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        handlers=[consola, archivo],
    )


# Contrato del archivo de pólizas: las 12 columnas que tiene que traer
COLUMNAS_FREQ = {"IDpol", "ClaimNb", "Exposure", "Area", "VehPower", "VehAge",
                 "DrivAge", "BonusMalus", "VehBrand", "VehGas", "Density", "Region"}

# Contrato del archivo de siniestros: las 2 columnas que tiene que traer
COLUMNAS_SEV = {"IDpol", "ClaimAmount"}


def validar_estructura(ruta: Path, columnas_esperadas: set):
    """Estructura común a los dos archivos: existe, columnas exactas y tiene filas.
    Se escribe una vez y la usan validar_freq y validar_sev."""
    if not ruta.exists():
        return None, [f"no existe el archivo {ruta}"]

    df = pd.read_csv(ruta)
    faltan = columnas_esperadas - set(df.columns)
    sobran = set(df.columns) - columnas_esperadas

    problemas = []
    if faltan:
        problemas.append(f"faltan columnas: {sorted(faltan)}")
    if sobran:
        problemas.append(f"sobran columnas: {sorted(sobran)}")
    if len(df) == 0:
        problemas.append("el archivo no tiene filas")

    return df, problemas


def validar_freq(ruta: Path):
    """Valida el CSV de pólizas contra su contrato. Devuelve (df, problemas)."""

    # --- ESTRUCTURA: si algo falla, se para aquí ---
    df, problemas = validar_estructura(ruta, COLUMNAS_FREQ)
    if problemas:
        return df, problemas

    # --- CONTENIDO: se anotan todos los problemas, no solo el primero ---
    n_idpol_vacio = df["IDpol"].isna().sum()
    if n_idpol_vacio > 0:
        problemas.append(f"IDpol vacío en {n_idpol_vacio} filas")

    n_idpol_repetido = df["IDpol"].duplicated().sum()
    if n_idpol_repetido > 0:
        problemas.append(f"IDpol repetido en {n_idpol_repetido} filas")

    n_claimnb_negativo = (df["ClaimNb"] < 0).sum()
    if n_claimnb_negativo > 0:
        problemas.append(f"ClaimNb negativo en {n_claimnb_negativo} filas")

    n_exposure_no_positiva = (df["Exposure"] <= 0).sum()
    if n_exposure_no_positiva > 0:
        problemas.append(f"Exposure menor o igual a 0 en {n_exposure_no_positiva} filas")

    # Decisión del bloque 1: las pólizas con Exposure > 1 año se CARGAN AVISANDO.
    # No rompen nada técnico, pero inflan el denominador de la frecuencia si son
    # error de datos. Entran en raw y negocio decide después qué hacer con ellas.
    n_exposure_mas_1 = (df["Exposure"] > 1).sum()
    if n_exposure_mas_1 > 0:
        log.warning(
            f"{n_exposure_mas_1} pólizas con Exposure > 1 año: se cargan, "
            f"revisar con negocio si son error de datos"
        )

    log.debug(f"validar_freq terminó: {len(problemas)} problemas de contenido")
    return df, problemas


def validar_sev(ruta: Path):
    """Valida el CSV de siniestros con SUS reglas, no las de pólizas. Devuelve (df, problemas)."""

    # --- ESTRUCTURA: la misma función que pólizas, con sus 2 columnas ---
    df, problemas = validar_estructura(ruta, COLUMNAS_SEV)
    if problemas:
        return df, problemas

    # --- CONTENIDO: reglas decididas en el bloque 3 ---
    # Regla 1 (PARA): IDpol sin vacíos. Sin IDpol el siniestro no se puede unir con su póliza.
    n_idpol_vacio = df["IDpol"].isna().sum()
    if n_idpol_vacio > 0:
        problemas.append(f"IDpol vacío en {n_idpol_vacio} filas")

    # Regla 2 (NO APLICA): IDpol repetido NO es un problema en siniestros.
    # Una póliza puede tener varios siniestros en el año (perfilado: pólizas con 11 y 16).

    # Regla 3 (PARA): ClaimAmount > 0. Un importe 0 o negativo no tiene sentido sin
    # una columna de estado (p. ej. siniestro anulado), y este archivo no la trae.
    n_importe_no_positivo = (df["ClaimAmount"] <= 0).sum()
    if n_importe_no_positivo > 0:
        problemas.append(f"ClaimAmount menor o igual a 0 en {n_importe_no_positivo} filas")

    # Regla 4 (NO APLICA): sin tope máximo de ClaimAmount. Hay siniestros legítimos de
    # millones (p. ej. pérdida total de una flotilla bajo una misma póliza).

    log.debug(f"validar_sev terminó: {len(problemas)} problemas de contenido")
    return df, problemas


def registrar(ruta: Path, df, problemas):
    """Deja en el log el resultado de validar un archivo."""
    if df is not None:
        log.info(f"leído {ruta.name}: {len(df)} filas")
    if problemas:
        for problema in problemas:  # cada problema, una línea ERROR
            log.error(f"{ruta.name}: {problema}")
    else:
        log.info(f"{ruta.name}: sin problemas, se puede cargar")


RUTAS = {
    "fremtpl2_freq": Path("data/fremtpl2_freq.csv"),
    "fremtpl2_sev": Path("data/fremtpl2_sev.csv"),
}


VOLUMEN = "/Volumes/workspace/raw/landing"


def conectar():
    """Las tres credenciales salen del entorno, nunca del código."""
    return sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
        staging_allowed_local_path=str(Path("data").resolve()),
    )


def cargar(cursor, tabla, ruta):
    """Sube el archivo al volumen y reconstruye con él la tabla de raw."""
    destino = f"{VOLUMEN}/{ruta.name}"
    cursor.execute(f"PUT '{ruta.resolve()}' INTO '{destino}' OVERWRITE")
    log.info(f"{ruta.name} subido a {destino}")
    cursor.execute(
        f"CREATE OR REPLACE TABLE workspace.raw.{tabla} AS "
        f"SELECT *, current_timestamp() AS _loaded_at "
        f"FROM read_files('{destino}', format => 'csv')"
    )
    cursor.execute(f"SELECT count(*) FROM workspace.raw.{tabla}")
    filas = cursor.fetchone()[0]
    log.info(f"workspace.raw.{tabla}: {filas} filas cargadas")
    return filas


def cargar_todo(resumen):
    with conectar() as conexion, conexion.cursor() as cursor:
        for tabla, ruta in RUTAS.items():
            resumen["archivos"][ruta.name]["filas_cargadas"] = cargar(cursor, tabla, ruta)


def main():
    configurar_logging()
    resumen = {"inicio": datetime.now().isoformat(timespec="seconds"), "archivos": {}}

    # 1. Validar los dos archivos. Si uno falla, no se carga ninguno.
    # En cada vuelta, validar es una de tus dos funciones: en Python una función
    # se puede guardar en una lista, como cualquier valor, y llamarse después.
    hay_problemas = False
    for tabla, validar in [("fremtpl2_freq", validar_freq), ("fremtpl2_sev", validar_sev)]:
        ruta = RUTAS[tabla]
        df, problemas = validar(ruta)
        registrar(ruta, df, problemas)
        resumen["archivos"][ruta.name] = {"filas_leidas": None if df is None else len(df),
                                          "problemas": problemas}
        if problemas:
            hay_problemas = True

    # 2. Decidir: con problemas, no se toca workspace.raw.
    if hay_problemas:
        log.error("carga detenida: hay problemas de validación, workspace.raw no se toca")
        codigo = 1
    else:
        cargar_todo(resumen)
        log.info("carga terminada")
        codigo = 0

    # 3. Dejar el resumen para quien venga detrás.
    resumen["fin"] = datetime.now().isoformat(timespec="seconds")
    resumen["codigo_salida"] = codigo
    Path("logs/ultima_carga.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
