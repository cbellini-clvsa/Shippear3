# Arquitectura

## Visión general

```
Usuario ──► Next.js (Vercel) ──► Postgres ◄── Python (data/)
              │  UI + rutas API        ▲        series macro
              │  sin login (abierta)   │
              └── lee content/*.json ──┘ (contenido versionado en el repo)
  progreso del recorrido: en el navegador (localStorage), sin identificar a nadie
```

## Decisiones y por qué

1. **El contenido vive en el repo (`content/`), no en la base.** Quien escribe lecciones y preguntas
   no depende de la base ni del backend, y el frontend se puede construir contra los JSON desde el minuto uno.
2. **No hay cuentas ni login (decisión 2026-10-24: app libre y abierta).** La base guarda solo las
   series macro. Lo que la persona responde, elige o completa vive en **su navegador** (localStorage),
   sin identificarla; no se sincroniza entre dispositivos.
3. **Prisma es dueño del esquema.** Python solo inserta filas en las tablas de series macro; no crea ni modifica tablas.
4. **Un solo servicio web.** Las rutas de API están dentro de Next.js. No hay un segundo servidor que desplegar.
5. **Python es un script, no un servidor.** Se ejecuta a mano o programado y escribe en la base.
   Si deciden no usar datos macro en vivo, Python se puede quitar sin tocar el resto.
6. **El puntaje y el nivel los calcula código determinista**, nunca la IA.

## Modelo de datos (propuesta)

| Tabla | Campos clave |
|---|---|
| `MacroSeries` | id (`ipc_mensual`, `dolar_oficial`…), name, unit |
| `MacroPoint` | seriesId, date, value |

No hay tablas de usuario. El estado del recorrido se guarda en el navegador con esta forma
(clave única de la app, versionada):

```json
{ "v": 1, "level": "principiante", "goal": "salir-de-deudas",
  "lessons": { "<moduleId>/<lessonId>": { "completedAt": "...", "miniTestScore": 8 } } }
```

`moduleId` y `lessonId` son los `id` de los archivos en `content/`.

## Contratos de API (acordarlos en los primeros 20 minutos)

| Método y ruta | Entrada | Salida |
|---|---|---|
| `POST /api/quiz/submit` | `{ answers: { [questionId]: optionId } }` | `{ score, level }` (no guarda nada; el cliente persiste el resultado) |
| `GET /api/macro/latest` | (nada) | `{ [seriesId]: { date, value } }` |

Objetivo elegido y progreso de lecciones **no pasan por la API**: se leen y escriben en el navegador.
Mientras A no tenga la API lista, B trabaja con respuestas simuladas con esta misma forma.

## Sin cuentas: cómo se maneja el progreso

- Todo se guarda en `localStorage` bajo una clave única y versionada; leer y escribir siempre con
  `try/catch` para que la app funcione aunque el navegador bloquee el almacenamiento.
- No se sincroniza entre dispositivos ni sobrevive a "borrar datos del sitio": decirlo en la app.
- Ofrecer un botón "Borrar mi progreso". Exportar/importar el progreso queda como mejora futura.

## Datos personales

No se guarda ningún dato personal en el servidor: no hay cuentas, email ni contraseñas. Mostrar un
aviso claro de que el progreso queda en el navegador y de que el contenido es educativo, no
asesoramiento financiero.
