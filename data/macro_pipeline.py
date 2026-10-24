"""Pipeline de datos macro.

Prisma es dueño del esquema: este script solo inserta filas en MacroSeries y MacroPoint.
Completar los TODO después de verificar qué series expone la fuente.
"""

import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# TODO: confirmar ids, nombres y endpoints reales en el catálogo de APIs del BCRA.
SERIES = {
    "ipc_mensual": {"name": "IPC mensual", "unit": "%"},
    "dolar_oficial": {"name": "Dólar oficial", "unit": "ARS"},
}


def fetch_series(series_id: str) -> pd.DataFrame:
    """Devuelve un DataFrame con columnas: date, value."""
    raise NotImplementedError(
        f"Verificar el endpoint de '{series_id}' en el catálogo de APIs del BCRA."
    )


def load_fixture(path: str = "fixtures/macro_seed.csv") -> pd.DataFrame:
    """Plan B: carga valores verificados a mano. Columnas: series,date,value."""
    return pd.read_csv(path, parse_dates=["date"])


def save(df: pd.DataFrame, series_id: str) -> None:
    """Inserta los puntos en MacroPoint (con SQLAlchemy y DATABASE_URL)."""
    raise NotImplementedError("Implementar la escritura una vez definido el esquema de Prisma.")


def main() -> None:
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("Falta DATABASE_URL en data/.env")
    for series_id in SERIES:
        df = fetch_series(series_id)
        save(df, series_id)


if __name__ == "__main__":
    main()
