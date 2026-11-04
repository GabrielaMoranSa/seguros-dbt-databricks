"""Generador del ciclo de vida: el sistema origen sintético del proyecto.

freMTPL2 es una foto: no trae fechas, ni primas, ni nada que le pase a una póliza con el tiempo. Este programa
hace de sistema de pólizas y siniestros de una aseguradora: a partir de las pólizas reales de data/fremtpl2_freq.csv
inventa lo que les pasa día a día, y deja cada día un lote con dos archivos en data/lotes/.

Es una herramienta aportada al proyecto, escrita por el mentor, no parte del trabajo de modelado: los datos que escribe son sintéticos.

Uso, desde la raíz del repo:
    python scripts/generar_lotes.py --desde 2026-01-01 --dias 30
"""
import argparse
import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

CARTERA = Path("data/fremtpl2_freq.csv")
SALIDA = Path("data/lotes")
INICIO = date(2026, 1, 1)        # el primer día de la vida de la cartera sintética
N_POLIZAS = 30_000               # cuántas pólizas de la cartera real entran en el ciclo de vida
DIAS_DE_ALTAS = 30               # las altas se reparten en los primeros 30 días
HORIZONTE = 400                  # hasta dónde se inventa la vida de cada póliza, en días
FRECUENCIA_ANUAL = 0.10          # siniestros por año de exposición, como la cartera real

COLUMNAS_POLIZAS = ["movimiento_id", "poliza_id", "tipo", "fecha_movimiento", "fecha_efecto", "prima_anual"]
COLUMNAS_SINIESTROS = ["movimiento_id", "siniestro_id", "poliza_id", "tipo", "fecha_ocurrencia",
                       "fecha_declaracion", "fecha_movimiento", "cambio_reserva", "pago"]


def leer_cartera(ruta):
    """Elige las pólizas que entran en el ciclo de vida. Siempre las mismas: el orden y la semilla están fijos."""
    with open(ruta, encoding="utf-8", newline="") as archivo:
        filas = {int(float(f["IDpol"])): f for f in csv.DictReader(archivo)}
    elegidas = random.Random(2026).sample(sorted(filas), N_POLIZAS)
    return [filas[poliza] for poliza in sorted(elegidas)]


def prima_inicial(fila, rng):
    """Una prima anual inventada: freMTPL2 no la trae. Sube con el bonus-malus y con la potencia del vehículo."""
    base = 180 + 22 * int(float(fila["VehPower"]))
    return round(base * int(float(fila["BonusMalus"])) / 100 * rng.uniform(0.9, 1.1), 2)


def vida_poliza(fila, semilla):
    """Todo lo que le pasa a una póliza, en orden. Devuelve sus movimientos y sus periodos con cobertura.

    Estados: ALTA deja la póliza vigente · SUPLEMENTO le cambia la prima y sigue vigente · ANULACION la deja sin
    cobertura · REHABILITACION se la devuelve. Una anulación se registra a veces días después de su fecha de efecto.
    """
    poliza = int(float(fila["IDpol"]))
    rng = random.Random(f"{semilla}-{poliza}")
    alta = INICIO + timedelta(days=rng.randrange(DIAS_DE_ALTAS))
    prima = prima_inicial(fila, rng)
    movs = [("ALTA", alta, alta, prima)]

    anulada = alta + timedelta(days=rng.randint(5, 60)) if rng.random() < 0.06 else None
    if rng.random() < 0.12:
        efecto = alta + timedelta(days=rng.randint(1, 60))
        if anulada is None or efecto < anulada:           # a una póliza anulada no se le hacen suplementos
            prima = round(prima * rng.uniform(0.9, 1.25), 2)
            movs.append(("SUPLEMENTO", efecto, efecto, prima))

    periodos = [(alta, alta + timedelta(days=HORIZONTE))]
    if anulada is not None:
        registrado = anulada + timedelta(days=rng.choice([0, 0, 0, 1, 2, 5, 10]))
        movs.append(("ANULACION", registrado, anulada, prima))
        periodos = [(alta, anulada)]
        if rng.random() < 0.35:
            vuelta = max(anulada + timedelta(days=rng.randint(3, 25)), registrado + timedelta(days=1))
            movs.append(("REHABILITACION", vuelta, vuelta, prima))
            periodos.append((vuelta, alta + timedelta(days=HORIZONTE)))

    filas = [{"poliza_id": poliza, "tipo": tipo, "fecha_movimiento": registrado, "fecha_efecto": efecto,
              "prima_anual": importe} for tipo, registrado, efecto, importe in movs]
    for n, mov in enumerate(filas, start=1):
        mov["movimiento_id"] = f"P{poliza}-{n}"
    return filas, periodos


def vida_siniestro(poliza, n, ocurrencia, rng):
    """Los movimientos de un siniestro: se abre con una reserva, se ajusta, se paga y se cierra.

    cambio_reserva sube o baja lo que queda reservado; pago es lo que sale de la caja y baja la reserva lo mismo, hasta dejarla en 0: si se paga más de lo reservado, sube el incurrido.
    Coste incurrido en cualquier fecha = pagos hasta esa fecha + reserva que queda. Al cerrar, la reserva vuelve a 0.
    """
    declaracion = ocurrencia + timedelta(days=rng.choice([0, 0, 1, 1, 2, 3, 5, 8, 13, 21, 34]))
    siniestro = f"S{poliza}-{n}"
    coste = round(rng.lognormvariate(7.0, 1.1), 2)
    reserva = round(coste * rng.uniform(0.7, 1.4), 2)
    dia = declaracion
    movs = [("APERTURA", dia, reserva, 0.0)]
    saldo = reserva

    if rng.random() < 0.4:                              # a veces la reserva se revisa cuando se sabe más
        dia += timedelta(days=rng.randint(2, 10))
        nueva = round(coste * rng.uniform(0.9, 1.2), 2)
        movs.append(("AJUSTE_RESERVA", dia, round(nueva - saldo, 2), 0.0))
        saldo = nueva

    pendiente = coste
    for parte in range(rng.choice([1, 1, 2, 3]), 0, -1):  # uno, dos o tres pagos, hasta completar el coste
        dia += timedelta(days=rng.randint(2, 15))
        pago = pendiente if parte == 1 else round(pendiente * rng.uniform(0.3, 0.6), 2)
        pendiente = round(pendiente - pago, 2)
        baja = min(saldo, pago)
        movs.append(("PAGO", dia, round(-baja, 2), pago))
        saldo = round(saldo - baja, 2)

    dia += timedelta(days=rng.randint(0, 5))
    movs.append(("CIERRE", dia, round(-saldo, 2), 0.0))    # la reserva que sobra se libera

    return [{"movimiento_id": f"{siniestro}-{i}", "siniestro_id": siniestro, "poliza_id": poliza, "tipo": tipo,
             "fecha_ocurrencia": ocurrencia, "fecha_declaracion": declaracion, "fecha_movimiento": fecha,
             "cambio_reserva": cambio, "pago": pagado}
            for i, (tipo, fecha, cambio, pagado) in enumerate(movs, start=1)]


def siniestros_de(poliza, periodos, semilla):
    """Los siniestros de una póliza, dentro de sus periodos con cobertura; en algunas rehabilitadas, uno en el hueco."""
    rng = random.Random(f"{semilla}-siniestros-{poliza}")
    movs, n = [], 0
    for inicio, fin in periodos:
        dia = inicio
        while True:
            dia += timedelta(days=int(rng.expovariate(FRECUENCIA_ANUAL / 365)) + 1)
            if dia >= fin:
                break
            n += 1
            movs += vida_siniestro(poliza, n, dia, rng)
    if len(periodos) == 2 and rng.random() < 0.40:       # un siniestro ocurrido mientras la póliza estaba anulada
        hueco = periodos[0][1] + timedelta(days=1)
        if hueco < periodos[1][0]:
            n += 1
            movs += vida_siniestro(poliza, n, hueco, rng)
    return movs


def inventar_todo(cartera, semilla):
    """La vida entera de todas las pólizas."""
    polizas, siniestros = [], []
    for fila in cartera:
        movs, periodos = vida_poliza(fila, semilla)
        polizas += movs
        siniestros += siniestros_de(movs[0]["poliza_id"], periodos, semilla)
    return polizas, siniestros


def escribir(ruta, columnas, filas):
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)


def escribir_lote(fecha, polizas, siniestros, salida):
    """Un lote: lo que se registró ese día, en dos archivos. Si ya existían, se reescriben con lo mismo.
    Un día sin movimientos de un tipo no deja archivo de ese tipo."""
    orden = lambda m: m["movimiento_id"]
    de_polizas = sorted((m for m in polizas if m["fecha_movimiento"] == fecha), key=orden)
    de_siniestros = sorted((m for m in siniestros if m["fecha_movimiento"] == fecha), key=orden)
    if de_polizas:
        escribir(salida / f"mov_polizas_{fecha}.csv", COLUMNAS_POLIZAS, de_polizas)
    if de_siniestros:
        escribir(salida / f"mov_siniestros_{fecha}.csv", COLUMNAS_SINIESTROS, de_siniestros)
    return len(de_polizas), len(de_siniestros)


def leer_argumentos(argv=None):
    """Lo que se puede pedir al lanzarlo. Cada opción tiene un valor por defecto, salvo la fecha y los días."""
    parser = argparse.ArgumentParser(description="Genera los lotes diarios del ciclo de vida de las pólizas.")
    parser.add_argument("--desde", type=date.fromisoformat, required=True, help="primer día, AAAA-MM-DD")
    parser.add_argument("--dias", type=int, required=True, help="cuántos días de lotes")
    parser.add_argument("--semilla", type=int, default=2026, help="número del que parte el azar (por defecto, 2026)")
    parser.add_argument("--salida", type=Path, default=SALIDA, help="carpeta de los lotes (por defecto, data/lotes)")
    args = parser.parse_args(argv)
    if args.dias < 1:
        parser.error("--dias tiene que ser 1 o más")
    return args


def main(argv=None):
    args = leer_argumentos(argv)
    args.salida.mkdir(parents=True, exist_ok=True)
    polizas, siniestros = inventar_todo(leer_cartera(CARTERA), args.semilla)
    total_p = total_s = 0
    for d in range(args.dias):
        fecha = args.desde + timedelta(days=d)
        n_p, n_s = escribir_lote(fecha, polizas, siniestros, args.salida)
        total_p += n_p
        total_s += n_s
    print(f"{args.dias} lotes en {args.salida}: {total_p} movimientos de póliza y {total_s} de siniestro")
    return 0


if __name__ == "__main__":
    sys.exit(main())
