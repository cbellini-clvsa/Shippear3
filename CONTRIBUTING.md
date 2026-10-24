# Cómo trabajamos en el mismo repo

Somos 3 personas y pocas horas. El objetivo es **no pisarnos** y **integrar seguido**.

## Reglas

1. **Cada uno tiene su carpeta** (ver tabla). Si necesitas tocar la de otro, avísale primero.
2. **Nadie pushea directo a `main`**, salvo A en la configuración inicial. Todo entra por Pull Request.
3. **Ramas cortas**: se abren, se integran en menos de una hora y se borran.
4. **PR chicos y revisión rápida**: otro del equipo mira en menos de 10 minutos. Si no se rompe nada, se mergea.
5. **Nunca se sube un `.env`**. Los secretos se pasan por un canal privado y A los carga en Vercel.
6. **Congelamiento**: a partir de la hora indicada en `docs/PLAN-4H.md` no se agregan funciones, solo arreglos.

## Quién es dueño de qué

| Ruta | Dueño | Nota |
|---|---|---|
| `apps/web/src/app/api/**`, `apps/web/prisma/**`, auth | A | Contratos en `docs/ARCHITECTURE.md` |
| `apps/web/src/app/(pantallas)/**`, `apps/web/src/components/**` | B | Lo generado en v0 entra acá |
| `content/**`, `data/**`, `docs/**` | C | |
| `package.json`, `schema.prisma`, `layout.tsx` | A | Archivos que causan más conflictos: pedir cambios a A |

## Flujo diario

```bash
# 1. Arrancar desde main actualizado
git switch main
git pull --rebase

# 2. Rama nueva, con el área y el tema
git switch -c feat/ui-resultado-cuestionario

# 3. Trabajar con commits chicos
git add -A
git commit -m "feat(ui): pantalla de resultado del cuestionario"

# 4. Antes de subir, traer lo último de main
git fetch origin
git rebase origin/main

# 5. Subir y abrir el Pull Request en GitHub
git push -u origin feat/ui-resultado-cuestionario
```

Prefijos de commit: `feat`, `fix`, `docs`, `chore`, `content`, `data`.

## Si hay conflicto

```bash
git status                      # ver qué archivos
# editar el archivo y dejar la versión correcta (sin <<<<<<<)
git add <archivo>
git rebase --continue
```

Si no estás seguro de qué versión conservar, **pregúntale al dueño del archivo** antes de resolver.

## Vercel y v0

- Si el repo está conectado a Vercel, cada Pull Request suele tener su propio enlace de vista previa.
  Úsenlo para revisar antes de mergear.
- Lo que genera v0 se copia a `apps/web/src/components` o a la pantalla correspondiente, se revisa,
  y entra por PR como cualquier otro cambio. No dejen que una regeneración pise páginas existentes sin revisar.
