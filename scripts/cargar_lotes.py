"""Carga los lotes del ciclo de vida en workspace.raw. Mismo camino que el loader de freMTPL2.

Sube cada archivo de data/lotes/ al volumen y reconstruye con todos ellos las dos tablas de raw. Se puede lanzar
las veces que haga falta: los archivos se pisan por su nombre y la tabla se reconstruye entera.

Uso, desde la raíz del repo y con las tres variables de entorno:
    python scripts/cargar_lotes.py
"""
import logging
import sys
from pathlib import Path

from cargar_fremtpl2 import VOLUMEN, conectar, configurar_logging
from generar_lotes import COLUMNAS_POLIZAS, COLUMNAS_SINIESTROS
from validaciones import validar_estructura

log = logging.getLogger("loader")
LOTES = Path("data/lotes")
TABLAS = {"mov_polizas": set(COLUMNAS_POLIZAS), "mov_siniestros": set(COLUMNAS_SINIESTROS)}


def validar_lotes(prefijo, columnas):
    """Todos los archivos de un tipo, con sus columnas. Devuelve las rutas y los problemas que haya."""
    rutas = sorted(LOTES.glob(f"{prefijo}_*.csv"))
    problemas = [] if rutas else [f"no hay archivos {prefijo}_*.csv en {LOTES}"]
    for ruta in rutas:
        _, de_este = validar_estructura(ruta, columnas)
        problemas += [f"{ruta.name}: {p}" for p in de_este]
    return rutas, problemas


def cargar_tabla(cursor, tabla, rutas):
    """Sube los archivos al volumen y reconstruye la tabla con todos los que haya allí."""
    for ruta in rutas:
        cursor.execute(f"PUT '{ruta.resolve()}' INTO '{VOLUMEN}/{ruta.name}' OVERWRITE")
    log.info(f"{tabla}: {len(rutas)} archivos subidos a {VOLUMEN}")
    cursor.execute(
        f"CREATE OR REPLACE TABLE workspace.raw.{tabla} AS "
        f"SELECT *, current_timestamp() AS _loaded_at "
        f"FROM read_files('{VOLUMEN}/{tabla}_*.csv', format => 'csv', header => true)"
    )
    cursor.execute(f"SELECT count(*) FROM workspace.raw.{tabla}")
    filas = cursor.fetchone()[0]
    log.info(f"workspace.raw.{tabla}: {filas} filas cargadas")
    return filas


def main():
    configurar_logging()
    log.info("carga de lotes: empieza")
    a_cargar, hay_problemas = {}, False
    for tabla, columnas in TABLAS.items():
        rutas, problemas = validar_lotes(tabla, columnas)
        a_cargar[tabla] = rutas
        for problema in problemas:
            log.error(problema)
            hay_problemas = True
    if hay_problemas:
        log.error("carga detenida: hay problemas de validación, workspace.raw no se toca")
        return 1
    try:
        with conectar() as conexion, conexion.cursor() as cursor:
            for tabla, rutas in a_cargar.items():
                cargar_tabla(cursor, tabla, rutas)
    except Exception:
        log.exception("carga interrumpida por un error inesperado")
        return 1
    log.info("carga de lotes terminada")
    return 0


if __name__ == "__main__":
    sys.exit(main())
