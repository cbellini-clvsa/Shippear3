# App de Capacitación Financiera — Diseño (Fase 1)

- **Fecha:** 2026-10-24
- **Estado:** Aprobado el enfoque general; pendiente revisión de esta especificación.
- **Nombre de trabajo:** `finanzas-app` (el nombre comercial definitivo es cosmético y se define más adelante; no bloquea nada).

---

## 1. Visión y objetivo

Una **app web gratuita de capacitación financiera** para el público general de **Argentina**, que
no sabe (o sabe poco) qué es una acción, una criptomoneda, el dólar, un fondo común de inversión o
variables macro como IPC, UVA o PBI. El objetivo es **orientar y capacitar**, en lenguaje llano, a
gente sin conocimientos previos.

La app se organiza alrededor de **tres patas** (recomendaciones):

1. **Educación financiera** — aprender qué es cada instrumento y cómo funciona.
2. **"Qué me corresponde" por perfil** — según la situación laboral/social de la persona (empleada
   doméstica, construcción, monotributista, etc.), qué derechos y obligaciones le marca la normativa
   vigente argentina.
3. **"Salir de deudas"** *(Fase 2, fuera del alcance de este documento)* — la persona sube una foto o
   captura (resumen de tarjeta, boleta de expensas/impuestos, captura de un portal de un organismo),
   la app la lee (OCR/IA), ordena las deudas y la orienta para salir.

**Público objetivo:** adultos en Argentina sin formación financiera, usando principalmente una PC
(con buena vista también en celular). Uso **anónimo**, sin registro.

---

## 2. Encuadre responsable (restricción transversal)

La app **orienta e informa; no da asesoramiento profesional personalizado.** Esto aplica a todo el
contenido y es una decisión de diseño, no un agregado opcional:

- **No** se dan recomendaciones de inversión personalizadas ("comprá esta acción") ni consejo legal
  personalizado ("demandá a tu empleador"). Se explica **qué es** cada cosa, **cómo funciona**, sus
  **riesgos** y **qué dice la normativa**.
- Todo dato legal/impositivo se muestra con su **fuente oficial** (ley, resolución, organismo) y la
  **fecha de verificación**.
- Aviso visible en las secciones sensibles: *"Esta información es orientativa y no reemplaza la
  consulta con un profesional (abogado/a, contador/a)."*
- La app **no accede a cuentas de nadie** en organismos ni bancos; en la Fase 2 el usuario aporta su
  propia captura.

Este encuadre protege al usuario y al responsable de la app, y evita cruzar a "asesoramiento
financiero/legal regulado".

---

## 3. Alcance

### En alcance (Fase 1)

- **Educación financiera:** módulos/lecciones por tema y nivel, glosario buscable, quizzes con
  puntaje.
- **Seguimiento de progreso sin cuentas:** se guarda en el navegador (localStorage).
- **Datos de mercado en vivo:** dólar (oficial/MEP/blue) + macro (IPC, UVA, inflación), con caché.
- **Catálogo de perfiles:** navegable por rubro, con derechos/obligaciones y fuentes por perfil.
- **Panel de administración:** carga/edición de todo el contenido sin tocar código (Django admin).
- **Contenido semilla inicial** cargado para que la app ya tenga sustancia.
- **Listo para desplegar gratis** en la nube.

### Fuera de alcance (Fase 2 u opcional, a diseñar aparte)

- **Escáner de deudas** (OCR/IA de documentos sensibles) y orientación para salir de deudas.
- **Acciones / Merval / CEDEARs** y **crypto** en vivo (diseñado para "sumar fácil" después).
- **Cuentas de usuario** y sincronización de progreso entre dispositivos.
- Multi-idioma (la app es en español).

---

## 4. Decisiones técnicas

| Decisión | Elección | Motivo |
|---|---|---|
| Lenguaje/Framework | **Python + Django** | Pedido del usuario (Python); Django trae ORM, migraciones y **admin automático** para cargar contenido sin código. |
| Base de datos | **SQLite** → **PostgreSQL** | SQLite para desarrollo (un archivo, cero config); Postgres al desplegar/crecer. El ORM de Django abstrae el cambio. |
| Frontend | **Plantillas server-side + JS liviano** | Simple, rápido, mantenible; no se justifica un SPA separado para contenido educativo. |
| Interactividad | JS puntual (quizzes, filtros, búsqueda del glosario) | Sin framework pesado de frontend. |
| Cuentas | **Ninguna** (anónimo) | Decisión del usuario; el progreso va al navegador. |
| Progreso | **localStorage** del navegador | Anónimo, sin backend de usuarios. Limitación asumida: por dispositivo. |
| Estilos | CSS propio liviano (o framework CSS mínimo) | Diseño limpio, sin dependencias pesadas. |

*Alternativas descartadas:* **FastAPI + React** (dos proyectos, sin admin gratis, overkill);
**Flask** (hay que construir a mano el admin que Django regala).

---

## 5. Arquitectura

Un **único proyecto Django** dividido en *apps* internas, cada una con una responsabilidad clara y
límites definidos. Esto hace el sistema fácil de entender, probar y extender pieza por pieza.

```
finanzas-app/
├── config/            # proyecto Django (settings, urls, wsgi)
├── core/              # home, páginas estáticas (acerca de, aviso legal), layout base
├── educacion/         # temas, módulos, lecciones
├── glosario/          # términos y sus relaciones
├── quizzes/           # quizzes, preguntas, opciones
├── mercado/           # servicio de datos en vivo (dólar, macro) + caché
├── perfiles/          # catálogo de perfiles laborales + fichas de derechos + fuentes
├── static/            # CSS, JS, imágenes
├── templates/         # plantillas HTML
├── docs/              # esta especificación y futuras
└── manage.py
```

Responsabilidad de cada app:

- **`core`** — arma la home (presenta las 3 patas), las páginas institucionales y el aviso legal; no
  tiene lógica de negocio pesada.
- **`educacion`** — organiza el contenido de aprendizaje en Temas → Módulos → Lecciones, por nivel.
- **`glosario`** — diccionario de términos con definiciones y enlaces entre términos relacionados.
- **`quizzes`** — preguntas de opción múltiple asociadas a un módulo/tema; corrige y da feedback.
- **`mercado`** — **no** es dueño de datos maestros: consulta APIs públicas, cachea y expone valores
  para mostrar. Aísla toda la dependencia de servicios externos en un solo lugar.
- **`perfiles`** — el catálogo "qué me corresponde": cada perfil con sus fichas y sus fuentes.

El **admin de Django** se habilita sobre `educacion`, `glosario`, `quizzes` y `perfiles` para la
gestión de contenido.

---

## 6. Modelo de datos (entidades principales)

> Campos a grandes rasgos; el detalle fino sale en la implementación. Todo contenido editable tiene
> un flag `publicado` para poder preparar borradores sin mostrarlos.

**educacion**
- `Tema` — nombre, slug, descripción, ícono, orden.
- `Modulo` — tema (FK), título, slug, nivel (principiante/intermedio/avanzado), resumen, orden,
  publicado.
- `Leccion` — módulo (FK), título, slug, contenido (texto enriquecido/Markdown), tiempo estimado,
  orden, publicado.

**glosario**
- `Termino` — palabra, slug, definición corta, definición larga, ejemplo, categoría,
  `relacionados` (M2M a sí mismo), publicado.

**quizzes**
- `Quiz` — título, descripción, módulo o tema asociado (FK, opcional), publicado.
- `Pregunta` — quiz (FK), enunciado, explicación (feedback al responder), orden.
- `Opcion` — pregunta (FK), texto, `es_correcta` (bool).

**perfiles**
- `Perfil` — nombre, slug, rubro/sector, descripción, ícono, orden, publicado.
- `FichaDerecho` — perfil (FK), categoría (p. ej. *encuadre legal*, *aportes y obra social*, *jornada
  y licencias*, *aguinaldo y vacaciones*, *ART*, *cómo formalizarse*), título, contenido, orden,
  `fuentes` (M2M a `Fuente`).
- `Fuente` — título (ley/resolución/organismo), tipo, `url_oficial`, `fecha_verificacion`, notas.

**mercado**
- Sin tabla maestra. Usa el **framework de caché** de Django para guardar los últimos valores
  traídos de las APIs, con su timestamp. (Opcional a futuro: una tabla de histórico, fuera de
  alcance ahora.)

---

## 7. Datos de mercado en vivo

- **Fuentes (Fase 1):** APIs públicas y gratuitas argentinas para **dólar** (oficial/MEP/blue) y
  **macro** (IPC, UVA, inflación). Candidatas conocidas: *dolarapi*, *ArgentinaDatos*, *BCRA
  Estadísticas*. La elección definitiva se valida al implementar (que estén vivas y sin clave).
- **Caché:** los valores se guardan unos minutos. Toda la app lee de la caché, no pega a la API en
  cada visita. Esto da velocidad y resiliencia.
- **Fallo de la API:** si una fuente no responde, se muestra el **último valor conocido con su fecha**
  (nunca un error crudo). Si no hay valor previo, se muestra un aviso de "dato no disponible ahora".
- **Encuadre:** los valores se muestran como **información**, con su fecha/hora de actualización.

---

## 8. Progreso sin cuentas (navegador)

- Se guarda en **localStorage**: lecciones leídas, módulos completados, quizzes aprobados y puntajes,
  y logros simples (p. ej. "completaste el nivel principiante").
- **Formato:** un objeto JSON versionado bajo una clave única de la app.
- **Limitaciones (comunicadas al usuario):** el progreso es **por dispositivo/navegador**; si borra
  los datos del navegador o cambia de PC, se pierde. Se avisa de forma clara y amable.
- **Degradación elegante:** si el navegador bloquea el almacenamiento (modo privado, etc.), la app
  igual funciona; simplemente no guarda el progreso.

---

## 9. Perfiles ("qué me corresponde")

- **Navegación:** catálogo navegable por rubro (decisión del usuario). La persona entra, ve la lista
  de perfiles, elige uno y lee su ficha; no hay cuestionario obligatorio.
- **Estructura de una ficha de perfil:** secciones por categoría (encuadre legal, aportes y obra
  social, jornada y licencias, aguinaldo/vacaciones, ART, cómo formalizarse…), cada una con su
  contenido y sus **fuentes con fecha**.
- **Perfiles iniciales (semilla):**
  1. Empleadas/os de casas particulares (Ley 26.844).
  2. Construcción / albañiles (Ley 22.250, UOCRA, fondo de cese laboral).
  3. Monotributistas (régimen de ARCA).
  4. Empleadas/os en relación de dependencia (LCT 20.744).
  5. Comercio (CCT 130/75, FAECYS).
  6. Trabajadoras/es rurales (Ley 26.727, UATRE/RENATRE).
- **Investigación de normativa:** el contenido legal vigente se investiga durante la construcción y
  se carga con sus fuentes oficiales y fecha. La normativa cambia seguido (montos, topes): por eso el
  modelo guarda `fecha_verificacion` y la UI la muestra.

---

## 10. Contenido semilla (lo que la app trae cargado el día 1)

- **Educación:** ~8–10 lecciones de los temas clave — qué es una acción, bonos, CEDEARs, fondos
  comunes de inversión, criptomonedas, el dólar y sus variantes, plazo fijo, inflación/IPC, UVA, PBI.
- **Glosario:** ~30–40 términos enlazados.
- **Quizzes:** uno por módulo inicial.
- **Perfiles:** los 6 listados arriba, con sus fichas y fuentes.

A partir de ahí, se suma todo el contenido que se quiera desde el **admin**, sin programar.

---

## 11. UX y navegación

- **Home:** presenta las 3 patas y accesos directos; muestra un vistazo de "Mercado hoy".
- **Aprender:** listado de temas → módulos → lecciones; glosario con buscador; quizzes.
- **Mercado hoy:** tarjetas con dólar y macro, con fecha de actualización.
- **Qué me corresponde:** catálogo de perfiles → ficha del perfil.
- **Diseño:** limpio y legible, pensado para PC y adaptable a celular (responsive). Lenguaje llano,
  sin jerga innecesaria; cuando aparece un término técnico, se enlaza al glosario.

---

## 12. Despliegue y hosting

- El proyecto se prepara para correr **local** (desarrollo, SQLite) y para **desplegar gratis** en la
  nube (Render / PythonAnywhere / Railway) con PostgreSQL.
- Configuración por **variables de entorno** (clave secreta, modo debug, base de datos), sin
  credenciales en el código.
- Archivos estáticos servidos de forma estándar para producción.

---

## 13. Seguridad y privacidad

- **Fase 1:** la app **no recolecta datos personales**. No hay cuentas; el progreso vive en el
  navegador del usuario. Mínima superficie de riesgo.
- **Buenas prácticas base:** HTTPS en producción, protección CSRF (que Django trae), sin secretos en
  el repositorio.
- **Fase 2 (principio ya fijado):** el escáner de deudas se diseñará con **privacidad máxima** — la
  imagen se procesa, se muestra el resumen y se descarta; **nunca** se guardan números de tarjeta,
  CUIT ni documentos.

---

## 14. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| La normativa cambia (montos, topes, leyes) | Modelo con `fecha_verificacion` + fuente visible; contenido editable desde el admin para actualizar rápido. |
| Una API de mercado cae o cambia | Toda la dependencia aislada en `mercado`; caché + último valor conocido; fácil cambiar de proveedor. |
| Precisión de la información legal/financiera | Encuadre responsable: fuentes oficiales, fecha y aviso de "no reemplaza a un profesional". |
| Que se interprete como asesoramiento regulado | Lenguaje informativo/educativo; sin recomendaciones personalizadas; avisos claros. |
| Que el proyecto se vuelva inmanejable por tamaño | Construcción por **fases**; apps con límites claros; la Fase 2 (la más pesada) se diseña aparte. |

---

## 15. Criterios de éxito (Fase 1)

- Una persona sin conocimientos puede entrar (sin registrarse), **leer una lección, hacer un quiz y
  ver su progreso** guardado al volver.
- Puede **ver el dólar y la inflación/IPC del día** con su fecha.
- Puede elegir su **perfil laboral** y leer, en lenguaje llano, **qué le corresponde** con la fuente
  y la fecha.
- El responsable de la app puede **cargar y editar contenido desde el admin** sin programar.
- El proyecto **arranca local** con un comando y está **listo para desplegar**.

---

## 16. Fase 2 (resumen, se diseña por separado)

"Salir de deudas": subida de imagen/captura → OCR/IA extrae los datos clave (monto, vencimiento,
interés) → resumen ordenado de deudas → orientación educativa para salir (conceptos como pago mínimo
e intereses, métodos de priorización, opciones de refinanciación y planes de pago oficiales). Dos
definiciones a tomar en esa etapa: **tecnología de lectura** (OCR gratuito vs. IA de visión, que
tiene costo por escaneo y choca con "gratuito") y el **detalle de privacidad** (principio ya fijado:
no guardar nada sensible).

---

## 17. Decisiones abiertas (menores, no bloquean)

- Nombre comercial de la app (cosmético).
- Framework CSS mínimo vs. CSS propio (se define al implementar la UI).
- Proveedor de hosting concreto (se elige al momento de publicar).
