# Plan de trabajo (supuesto: 4 horas, equipo de 3)

> Supuestos a confirmar: 4 horas de duración y el reparto de roles. Ajustar al equipo real.

## Roles

| Persona | Rol | Entrega |
|---|---|---|
| **A** | Base técnica | Repo, Next.js, Postgres con Prisma (series macro), rutas de API, deploy. Sin login: la app es abierta |
| **B** | Frontend | Pantallas con v0 y shadcn/ui, conectadas primero a datos simulados |
| **C** | Contenido y datos | `content/` (cuestionario y módulos), pipeline de datos macro, pitch y mapa del recorrido |

## Cronograma

| Tramo | A | B | C |
|---|---|---|---|
| 0:00 a 0:20 | **Todos juntos**: acordar esquema de `content/` y contratos de API | | |
| 0:20 a 0:50 | Repo en GitHub, Next.js, deploy vacío en Vercel | Esqueleto de pantallas en v0 | Cuestionario de 10 preguntas |
| 0:50 a 2:00 | Prisma (series macro), rutas de API, progreso en el navegador | Cuestionario, resultado, ruta de módulos | Módulos 1 y 2 con lecciones y mini-test |
| 2:00 a 3:00 | Integración con la UI, datos macro reales | Conectar a la API real, objetivos y avance guardados en el navegador | Módulos 3 y 4, datos macro cargados |
| 3:00 a 3:30 | Pruebas del recorrido completo, correcciones | Pulido visual | Guion de la demo |
| **3:30** | **Congelamiento** | | |
| 3:30 a 4:00 | Ensayo de la demo, plan B si falla la base de datos | | |

## Recorrido mínimo para la demo

1. Entra directo, sin registrarse (la app es abierta).
2. Responde el cuestionario y ve su nivel.
3. Elige un objetivo.
4. Ve su ruta de módulos y completa una lección con su mini-test.
5. Ve su avance actualizado (guardado en su navegador).

Si esto funciona de punta a punta, la demo funciona. Todo lo demás es opcional.

## Qué se recorta primero si falta tiempo

1. Tutor de IA.
2. Datos macro en vivo: pasar a valores cargados a mano.
3. Módulos 3 y 4.
4. Objetivos que reordenan la ruta: que solo se guarden.
