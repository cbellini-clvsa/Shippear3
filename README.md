# Educación financiera para todos (hackatón, rama financiera)

Web app de educación financiera para personas sin conocimientos previos, en Argentina.
La app es **libre y abierta al público: no hay registro ni login** (decisión del 2026-10-24).
El usuario responde un cuestionario de nivel, elige un objetivo y recorre módulos; el seguimiento
de avance por usuario queda fuera mientras no haya cuentas.

> Estado: esqueleto inicial. `apps/web` todavía no está inicializada (ver "Primeros pasos").

## Stack

| Capa | Tecnología | Quién la toca |
|---|---|---|
| Frontend + API | Next.js (App Router) + TypeScript + Tailwind + shadcn/ui | A (API), B (UI) |
| Login | **No hay**: app abierta, sin cuentas (decisión 2026-10-24) | — |
| Base de datos | Postgres (Neon o Supabase) + Prisma | A |
| Contenido | Archivos JSON versionados en `content/` | C |
| Datos macro | Python (pandas) que escribe en la base | C |
| Deploy | Vercel | A |

## Estructura

```
apps/web/       Next.js (frontend + rutas de API)
content/        Cuestionario y módulos en JSON (se versionan, no viven en la base)
data/           Pipeline Python de series macro (IPC, dólar, tasas)
docs/           Arquitectura y plan de trabajo
CONTRIBUTING.md Cómo trabajamos con git
```

## Primeros pasos (persona A)

```bash
cd apps
pnpm create next-app@latest web --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-pnpm
cd web
pnpm add next-auth zod @prisma/client
pnpm add -D prisma
pnpm dlx prisma init
```

Verifiquen las opciones del asistente y la guía de Auth.js (https://authjs.dev) porque
las versiones cambian. Después, copien `.env.example` a `apps/web/.env.local` y completen.

## Variables de entorno

Ver `.env.example`. Nunca se sube un `.env` real al repo.

## Documentación

- `docs/ARCHITECTURE.md`: decisiones, modelo de datos y contratos de API.
- `docs/PLAN-4H.md`: reparto de roles y cronograma.
- `CONTRIBUTING.md`: flujo de git y reglas del equipo.
# Shippear3
