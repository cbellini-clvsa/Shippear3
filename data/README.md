# Pipeline de datos macro (Python)

Descarga series macroeconómicas, las limpia con pandas y las escribe en la base.

## Regla importante

**Prisma es dueño del esquema.** Este script no crea ni modifica tablas: solo inserta filas
en `MacroSeries` y `MacroPoint`. Si necesitas una columna nueva, se pide a quien lleva Prisma.

## Antes de escribir código

Verificar qué series expone realmente la fuente y si exige token:
https://www.bcra.gob.ar/BCRAyVos/catalogo-de-APIs-banco-central.asp

Series candidatas: IPC mensual, dólar oficial, tasa de plazo fijo. Confirmar disponibilidad
antes de comprometerse con ellas.

## Uso

```bash
cd data
python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env            # completar DATABASE_URL
python macro_pipeline.py
```

## Plan B para la demo

Si la fuente falla el día de la presentación, cargar a mano `fixtures/macro_seed.csv`
(columnas `series,date,value`) con valores verificados. Una demo con datos fijos que funciona
es mejor que una demo con datos en vivo que falla.
