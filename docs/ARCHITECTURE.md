# Arquitectura

## Visión general

```
Usuario ──► Next.js (Vercel) ──► Postgres ◄── Python (data/)
              │  UI + rutas API        ▲        series macro
              │  Auth.js (Google)      │
              └── lee content/*.json ──┘ (contenido versionado en el repo)
```

## Decisiones y por qué

1. **El contenido vive en el repo (`content/`), no en la base.** Quien escribe lecciones y preguntas
   no depende de la base ni del backend, y el frontend se puede construir contra los JSON desde el minuto uno.
2. **La base guarda solo estado de usuario**: quién es, qué respondió, qué completó, qué objetivo eligió.
3. **Prisma es dueño del esquema.** Python solo inserta filas en las tablas de series macro; no crea ni modifica tablas.
4. **Un solo servicio web.** Las rutas de API están dentro de Next.js. No hay un segundo servidor que desplegar.
5. **Python es un script, no un servidor.** Se ejecuta a mano o programado y escribe en la base.
   Si deciden no usar datos macro en vivo, Python se puede quitar sin tocar el resto.
6. **El puntaje y el nivel los calcula código determinista**, nunca la IA.

## Modelo de datos (propuesta)

| Tabla | Campos clave |
|---|---|
| `User` | id, email, name, createdAt (lo gestiona Auth.js) |
| `QuizAttempt` | id, userId, score, level, answers (JSON), createdAt |
| `Goal` | id, userId, type (ej. `salir-de-deudas`), createdAt |
| `LessonProgress` | userId, moduleId, lessonId, completedAt, miniTestScore |
| `MacroSeries` | id (`ipc_mensual`, `dolar_oficial`…), name, unit |
| `MacroPoint` | seriesId, date, value |

`moduleId` y `lessonId` son los `id` de los archivos en `content/`.

## Contratos de API (acordarlos en los primeros 20 minutos)

| Método y ruta | Entrada | Salida |
|---|---|---|
| `POST /api/quiz/submit` | `{ answers: { [questionId]: optionId } }` | `{ score, level }` |
| `POST /api/goals` | `{ type }` | `{ ok: true }` |
| `GET /api/me/progress` | (sesión) | `{ level, goals, lessons: [...], percent }` |
| `POST /api/progress/lesson` | `{ moduleId, lessonId, miniTestScore? }` | `{ ok: true, percent }` |
| `GET /api/macro/latest` | (nada) | `{ [seriesId]: { date, value } }` |

Mientras A no tenga la API lista, B trabaja con respuestas simuladas con esta misma forma.

## Login con Google: puntos que suelen trabar

- Crear el ID de cliente OAuth en Google Cloud Console.
- Cargar **dos** URI de redireccionamiento autorizadas: la de local y la de producción.
  Con Auth.js la ruta suele ser `/api/auth/callback/google` (verificar en la guía vigente).
- Si la pantalla de consentimiento queda en modo de prueba, solo entran los correos cargados como
  usuarios de prueba. Carguen los correos de la demo antes de presentar.

## Datos personales

Se guarda email, respuestas y progreso. Mostrar un aviso claro en la app de qué se almacena
y que el contenido es educativo, no asesoramiento financiero.
