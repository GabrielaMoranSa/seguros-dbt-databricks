"""Las reglas de los dos archivos de freMTPL2: qué tiene que traer cada uno para poder cargarse.
Viven aquí, separadas del loader, para poder probarlas solas."""

import logging
from pathlib import Path

import pandas as pd

log = logging.getLogger("loader")

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