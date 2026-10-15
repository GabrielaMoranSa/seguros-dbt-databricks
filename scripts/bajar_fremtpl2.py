# Script: baja freMTPL2 (frecuencia y severidad) desde OpenML y lo guarda como CSV
from pathlib import Path
from sklearn.datasets import fetch_openml

# Carpeta donde se guardan los CSV (se crea si no existe)
SALIDA = Path("data")
SALIDA.mkdir(exist_ok=True)

# Las dos tablas: nombre del archivo e id en OpenML
for nombre, data_id in [("fremtpl2_freq", 41214), ("fremtpl2_sev", 41215)]:
    df = fetch_openml(data_id=data_id, as_frame=True).frame   # baja la tabla como DataFrame de pandas
    print(nombre, df.shape)                                   # filas y columnas
    print(df.dtypes)                                          # tipo de cada columna
    df.to_csv(SALIDA / f"{nombre}.csv", index=False)          # guarda el CSV