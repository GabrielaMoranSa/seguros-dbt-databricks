import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from databricks import sql
from validaciones import validar_freq, validar_sev
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
    codigo = 1
    try:
        # 1. Validar los dos archivos. Si uno falla, no se carga ninguno.
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
        else:
            cargar_todo(resumen)
            log.info("carga terminada")
            codigo = 0
    except Exception as error:
        # 3. Lo inesperado también deja rastro: el ERROR con su traceback, en el log.
        log.exception("carga interrumpida por un error inesperado")
        resumen["error"] = type(error).__name__
    finally:
        # 4. El resumen se escribe siempre, haya ido bien o mal.
        resumen["fin"] = datetime.now().isoformat(timespec="seconds")
        resumen["codigo_salida"] = codigo
        Path("logs/ultima_carga.json").write_text(
            json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    return codigo

if __name__ == "__main__":
    sys.exit(main())
