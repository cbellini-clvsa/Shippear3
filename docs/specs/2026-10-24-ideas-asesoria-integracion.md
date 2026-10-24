# Incorporar ideas de "Asesoría financiera para principiantes" a finanzas-app

- **Fecha:** 2026-10-24
- **Estado:** Propuesta. Pendiente de elegir qué ideas entran y en qué orden.
- **Origen:** `asesoria-financiera-principiantes.zip` — app Next.js 16 / React 19 + shadcn/ui
  (Tailwind), de educación financiera para principiantes, redactada en **español rioplatense**
  (registro "vos", llano). Autocontenida, todo corre en el navegador.
- **Destino:** `finanzas-app` — Python + Django, plantillas server-side + JS liviano
  (ver `docs/specs/2026-10-24-fase1-diseno.md`).

---

## 1. Idea central

El zip **no se copia tal cual**: su stack es React/Next.js y `finanzas-app` va en Django con
plantillas server-side + JS liviano. Lo que se incorpora son **ideas** — herramientas interactivas,
contenido ya redactado, estructura pedagógica y patrones de UX — **portadas** a la arquitectura de
`finanzas-app`. La buena noticia: casi todo encaja de lleno en la **pata educativa de la Fase 1**, y
la lógica de las herramientas es aritmética simple, fácil de reescribir en JS vanilla (lo que la
decisión técnica ya eligió: "Plantillas server-side + JS liviano").

> **Nota de stack.** El `README.md` viejo menciona Next.js + Prisma; la spec de hoy define Django.
> Acá se asume **Django** (es la decisión vigente). Si el equipo volviera a Next.js/React, varias
> piezas del zip serían casi *drop-in* (comparten shadcn/ui + Tailwind) — conviene decidirlo antes
> de portar.

---

## 2. Catálogo de ideas del zip

| # | Idea | Qué aporta | Encaje en finanzas-app (Django) | Alcance | Esfuerzo | Prioridad |
|---|---|---|---|---|---|---|
| A | **Calculadoras interactivas** (interés compuesto, meta de ahorro, fondo de emergencia) | Herramientas didácticas que "ponen números" a los conceptos; enganchan al usuario sin login | App/sección nueva `herramientas`: plantilla + JS liviano. Lógica = aritmética pura | Fase 1 ✅ | Medio | **Alta** |
| B | **Presupuesto 50/30/20** | Planificador con sliders y feedback por umbral; muy visual | Misma sección `herramientas`, JS liviano | Fase 1 ✅ | Bajo | **Alta** |
| C | **Glosario semilla** (8 términos ya redactados: inflación, interés compuesto, TNA/TEA, liquidez, diversificar, riesgo/rendimiento, fondo de emergencia, CFT) | Contenido listo para la app `glosario` (la spec pide 30–40 términos) | Filas del modelo `Termino` (fixture / seed) | Fase 1 ✅ | Muy bajo | **Alta** |
| D | **Roadmap "5 pasos, en este orden"** (gastos → emergencia → deudas → ahorro → inversión) | Columna vertebral pedagógica + "mapa del recorrido" (entregable del rol C en PLAN-4H) | `educacion`: un Tema "Ordená tu plata" o una página "Ruta" con 5 lecciones/tarjetas | Fase 1 ✅ | Bajo | **Alta** |
| E | **Test de perfil de ahorrista** (5 preguntas → conservador / moderado / dinámico + próximos pasos) | Engagement + autoconocimiento; distinto del quiz de **nivel** que ya existe | `quizzes` (variante "sin respuesta correcta, devuelve perfil") o mini-módulo propio | Fase 1 ✅ (con encuadre) | Medio | Media |
| F | **Plantillas de 5 pasos descargables** (registro de gastos, fondo, plan de deudas, ahorro automático, política de inversión) | Herramientas accionables que el usuario completa y se descarga | Sección `herramientas` / descargas; más "utilitario" que educativo | Fase 1 (liviano) o futuro | Medio | Media |
| G | **Simulador de deudas** (avalancha vs. bola de nieve) — `lib/debt.ts` + `python/debt.py` (stdlib, ya en Python) | Calculadora educativa de cómo conviene pagar varias deudas; el código Python ya está listo | Vista Django o comando; o portar a JS. **Ojo alcance** (ver §4) | Borderline (ver §4) | Medio | Media/Baja |
| H | **Tono y voz** (español rioplatense, llano: "tu yo del futuro te lo agradece") | Exactamente el registro que pide la spec; textos semilla (hints, feedback por umbral) | Guía de redacción + textos reutilizables en todo el contenido | Fase 1 ✅ | Muy bajo | Alta (transversal) |
| I | **Patrones de UX accesibles** (feedback `aria-live` por umbral, barras de proporción, resultados grandes `tabular-nums`, roles ARIA en tabs/progress) | Patrones de accesibilidad y claridad reutilizables | Guía de componentes para las plantillas Django | Fase 1 ✅ | Bajo | Media |

---

## 3. Mapa a las apps Django

- **`glosario`** → cargar los 8 términos del zip como semilla (idea C). Listos, solo adaptar al modelo.
- **`educacion`** → roadmap de 5 pasos como Tema/página "Ruta" (idea D); adoptar el tono (H).
- **`quizzes`** → test de perfil como variante que **no** corrige sino que **clasifica** (idea E).
  Requiere una pequeña extensión del modelo o un quiz "tipo perfil" (puntaje → rango → resultado).
- **App nueva `herramientas`** (sugerida) → calculadoras (A), presupuesto (B), plantillas (F),
  simulador de deudas (G). Todas client-side, sin tocar la base; encajan con "JS liviano".
- **`mercado`** → sin cambios; el zip no aporta nada acá.

---

## 4. Caveats transversales (leer antes de implementar)

1. **Encuadre responsable (spec §2).** El **test de perfil** y el **simulador de deudas** deben
   llevar el aviso *"Contenido educativo. No es asesoramiento de inversión."* y evitar el imperativo
   ("comprá X"). El zip ya lo plantea bien ("No hay respuestas correctas").
2. **Alcance del simulador de deudas.** La spec puso **"Salir de deudas (escáner)"** como fase
   futura (§15). El simulador del zip **no** es el escáner OCR: es una **calculadora educativa**
   (avalancha vs. bola de nieve) y como tal encaja en Fase 1. **Confirmar** si se incluye ahora o se
   deja junto con la futura pata de deudas.
3. **Nada de copiar React.** No se traen `.tsx`, ni Next, ni el runtime de shadcn. Se reescriben las
   plantillas en Django + JS vanilla. (La aritmética de `calculators.tsx`, `budget-planner.tsx` y
   `debt.py` es trivial de portar.)
4. **Sin login para las herramientas.** Calculadoras y presupuesto corren en el navegador; no
   necesitan cuenta ni base. Encaja con "explorar sin iniciar sesión".

---

## 5. Recomendación de orden

- **Batch 1 (rápido, alto valor, Fase 1):** C (glosario semilla) → D (roadmap 5 pasos) →
  A (calculadoras) → B (presupuesto 50/30/20). Más H (tono) como transversal.
- **Batch 2:** E (test de perfil, con encuadre) → F (plantillas descargables).
- **Batch 3 (confirmar alcance):** G (simulador de deudas educativo). La lógica Python ya existe.

El **Batch 1** da el mayor retorno con el menor riesgo: contenido semilla listo + tres herramientas
interactivas que no tocan base ni login.

---

## 6. Material del zip reutilizable directamente

- **8 términos de glosario** con definiciones (`components/glossary.tsx`).
- **5 pasos del roadmap** con título/cuerpo/tip (`components/roadmap.tsx`).
- **Test de perfil**: 5 preguntas + 3 perfiles + próximos pasos (`components/profile-quiz.tsx`).
- **Fórmulas** de interés compuesto mensual, meta de ahorro y fondo de emergencia
  (`components/calculators.tsx`) y presupuesto 50/30/20 (`components/budget-planner.tsx`).
- **Simulador de deudas en Python puro** (`python/debt.py`, solo stdlib) — portable casi directo a
  una vista Django o un comando de management.
