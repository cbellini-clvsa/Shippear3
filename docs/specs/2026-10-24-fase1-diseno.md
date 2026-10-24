# App de Educación Financiera Pública — Diseño (Fase 1)

- **Fecha:** 2026-10-24
- **Estado:** Enfoque acotado a educación financiera. **Decisión 2026-10-24: la app es libre y abierta al público, sin login ni cuentas** (se quitó el login con Google de la maqueta; este documento ya está alineado con esa decisión). Pendiente go-ahead al plan de implementación.
- **Nombre de trabajo:** `finanzas-app` (nombre comercial provisorio en la maqueta: "Plata Clara"; es cosmético y no bloquea nada).

---

## 1. Visión y objetivo

Una **app web gratuita de educación financiera** para el **público general de Argentina**, pensada
para gente **sin conocimientos previos**. Enseña, en lenguaje llano y desde cero, qué es y cómo
funciona cada instrumento y variable: acciones, criptomonedas, el dólar y sus variantes, plazo fijo,
fondos comunes de inversión (FCI), bonos, CEDEARs, e indicadores macro como **IPC, UVA y PBI**.

Uso gratuito y **sin registro**: no hay cuentas ni login; todo el contenido y las herramientas están
abiertos, y el progreso de cada persona se guarda **en su navegador**. Pensada para **PC** (con buena
vista también en celular).

> **Alcance acotado a propósito.** Esta Fase 1 es **solo la pata educativa**. Las ideas de
> "qué me corresponde por perfil laboral" y "salir de deudas (escáner)" quedan registradas como
> **posibles fases futuras** (sección 15), fuera del alcance de este documento.

---

## 2. Encuadre responsable (restricción transversal)

La app **educa e informa; no da asesoramiento de inversión personalizado.** Explica **qué es** cada
instrumento, **cómo funciona** y sus **riesgos**, pero nunca recomienda "comprá tal acción" ni arma
carteras a medida.

- Los **datos de mercado** se muestran como información, con su **fecha/hora de actualización**.
- Aviso visible en las secciones de inversión: *"Contenido educativo. No es asesoramiento de
  inversión; no reemplaza la consulta con un profesional."*
- La app **no accede a cuentas** bancarias ni de ningún organismo, y **no pide identificarse**: no hay
  login ni se guardan datos personales en el servidor (ver sección 12).

---

## 3. Alcance

### En alcance (Fase 1)

- **Educación financiera:** contenido organizado en Temas → Módulos → Lecciones, por nivel
  (principiante → intermedio → avanzado).
- **Glosario** buscable, con términos enlazados entre sí.
- **Quizzes** con puntaje y feedback, asociados a módulos.
- **Ruta "5 pasos, en este orden"** (gastos → emergencia → deudas → ahorro → inversión) y
  **Herramientas** interactivas (calculadoras de interés compuesto, meta de ahorro, fondo de
  emergencia y presupuesto 50/30/20), client-side y sin login. *(Ideas portadas del material de
  asesoría; ver `2026-10-24-ideas-asesoria-integracion.md`.)*
- **Progreso en el navegador, sin cuentas:** lecciones completadas, puntajes, racha y logros se
  guardan en el dispositivo de la persona (localStorage). No se sincronizan entre dispositivos y se
  pueden borrar desde la app.
- **Datos de mercado en vivo, agrupados:** **Dólar** (oficial/MEP/blue/CCL), **Acciones** (BYMA),
  **Bonos**, **Indicadores del Estado** (IPC, inflación interanual, UVA, riesgo país, actividad EMAE)
  y **Crypto**. Al tocar un instrumento se ve su **evolución mensual del último año**.
- **Panel de administración** para cargar/editar todo el contenido sin tocar código (Django admin).
- **Contenido semilla inicial** cargado.
- **Listo para desplegar gratis** en la nube.

### Fuera de alcance (futuro, a diseñar aparte)

- **Perfiles laborales** ("qué me corresponde" según normativa por rubro).
- **Escáner de deudas** (OCR/IA de documentos) y orientación para salir de deudas.
- **Acciones / Merval / CEDEARs** y **crypto** en vivo (diseñado para "sumar fácil" después).
- **Cuentas de usuario y login** de cualquier proveedor: la app es abierta por decisión. Si alguna
  vez hiciera falta sincronizar el progreso entre dispositivos, se diseña aparte.
- Multi-idioma (la app es en español).

---

## 4. Decisiones técnicas

| Decisión | Elección | Motivo |
|---|---|---|
| Lenguaje/Framework | **Python + Django** | Pedido del usuario (Python); Django trae ORM, migraciones y **admin automático** para cargar contenido sin código. |
| Base de datos | **SQLite** → **PostgreSQL** | SQLite para desarrollo (un archivo, cero config); Postgres al desplegar/crecer. El ORM de Django abstrae el cambio. |
| Frontend | **Plantillas server-side + JS liviano** | Simple, rápido, mantenible; no se justifica un SPA para contenido educativo. |
| Autenticación | **Ninguna** (app libre y abierta) | Decisión 2026-10-24: sin ningún tipo de acceso. Cero fricción, sin datos personales ni credenciales que administrar. |
| Progreso | **En el navegador** (localStorage) | Sin cuentas no hay otro lugar donde guardarlo; se asume que no se sincroniza entre dispositivos y se avisa. |
| Estilos | CSS propio liviano | Diseño limpio y colorido, sin dependencias pesadas. |

*Alternativas descartadas:* **FastAPI + React** (dos proyectos, sin admin gratis, overkill);
**Flask** (hay que construir a mano el admin que Django regala); **login con Google** (se llegó a
implementar en la maqueta y se descartó el 2026-10-24: la app tiene que ser libre y abierta, sin
ningún acceso).

---

## 5. Arquitectura

Un **único proyecto Django** dividido en *apps* internas, cada una con una responsabilidad clara.

```
finanzas-app/
├── config/            # proyecto Django (settings, urls, wsgi)
├── core/              # home, páginas estáticas (acerca de, aviso legal), layout base
├── educacion/         # temas, módulos, lecciones
├── glosario/          # términos y sus relaciones
├── quizzes/           # quizzes, preguntas, opciones
├── mercado/           # servicio de datos en vivo (dólar, macro) + caché
├── static/            # CSS, JS, imágenes
├── templates/         # plantillas HTML
├── docs/              # esta especificación y la maqueta
└── manage.py
```

Responsabilidad de cada app:

- **`core`** — arma la home, las páginas institucionales y el aviso legal; sin lógica de negocio pesada.
- *(No hay app de cuentas: no existe autenticación. El progreso se guarda en el navegador; ver
  sección 8.)*
- **`educacion`** — organiza el contenido en Temas → Módulos → Lecciones, por nivel.
- **`glosario`** — diccionario de términos con definiciones y enlaces entre términos relacionados.
- **`quizzes`** — preguntas de opción múltiple asociadas a un módulo; corrige y da feedback.
- **`mercado`** — **no** es dueño de datos maestros: consulta APIs públicas, cachea y expone valores.
  Aísla toda la dependencia de servicios externos en un solo lugar.

El **admin de Django** se habilita sobre `educacion`, `glosario` y `quizzes` para la gestión de
contenido.

---

## 6. Modelo de datos (entidades principales)

> Campos a grandes rasgos; el detalle fino sale en la implementación. Todo contenido editable tiene
> un flag `publicado` para preparar borradores sin mostrarlos.

**progreso**
- Sin tablas: no hay usuarios. Lecciones completadas, intentos de quiz, racha y logros se guardan en
  el navegador de cada persona (ver sección 8).

**educacion**
- `Tema` — nombre, slug, descripción, ícono, color, orden.
- `Modulo` — tema (FK), título, slug, nivel (principiante/intermedio/avanzado), resumen, orden,
  publicado.
- `Leccion` — módulo (FK), título, slug, contenido (texto enriquecido/Markdown), tiempo estimado,
  orden, publicado.

**glosario**
- `Termino` — palabra, slug, definición corta, definición larga, ejemplo, categoría,
  `relacionados` (M2M a sí mismo), publicado.

**quizzes**
- `Quiz` — título, descripción, módulo asociado (FK, opcional), publicado.
- `Pregunta` — quiz (FK), enunciado, explicación (feedback al responder), orden.
- `Opcion` — pregunta (FK), texto, `es_correcta` (bool).

**mercado**
- Sin tabla maestra. Usa el **framework de caché** de Django para guardar los últimos valores de las
  APIs con su timestamp. (Opcional a futuro: tabla de histórico, fuera de alcance.)

---

## 7. Datos de mercado en vivo (APIs públicas y gratuitas)

Los datos se muestran **agrupados**: **Dólar**, **Acciones**, **Bonos**, **Indicadores del Estado**
y **Crypto**. Al tocar un instrumento se ve su **evolución mensual del último año** (gráfico de líneas
con un punto por mes). Fuentes confirmadas y en uso (todas sin clave):

| Grupo | Dato | Fuente (API) |
|---|---|---|
| Dólar | oficial / blue / MEP / CCL (actual + histórico) | `dolarapi.com` + `api.argentinadatos.com` |
| Indicadores del Estado | IPC, inflación interanual, UVA, riesgo país | `api.argentinadatos.com` (datos INDEC/BCRA) |
| Indicadores del Estado | Actividad económica (EMAE, proxy mensual del PBI) | `apis.datos.gob.ar` (INDEC — **API oficial del Estado**) |
| Acciones | GGAL, YPFD, PAMP, ALUA, BMA, TXAR (BYMA) + histórico mensual | Yahoo Finance (gratuito) |
| Bonos | AL30/GD30/AL35/GD35/AE38/GD41 (precio del día) | `data912.com` (BYMA) |
| Crypto | BTC, ETH, SOL (actual + histórico) | `api.coingecko.com` |

- **Histórico mensual:** 12 puntos (un valor por mes del último año). Para **bonos**, la fuente
  gratuita solo da el precio del día; la serie histórica mensual de bonos se integra en la app real
  (se avisa en la ficha). **Crypto y Acciones** se muestran con **velas (candlestick) mensuales**
  (Lightweight Charts de TradingView); el resto, en línea.
- **Caché + resiliencia:** la app lee de una caché (unos minutos) y, si una fuente falla, muestra el
  **último valor conocido con su fecha**, nunca un error crudo.
- **En la maqueta** los valores van **embebidos** (reales, a la fecha de generación); en la app
  Django se **actualizan solos** desde estas mismas APIs.

---

## 8. Progreso (sin cuentas)

- **Dónde vive:** en el **navegador** de la persona (localStorage): lecciones completadas, puntajes
  de quizzes, racha de días y logros. No se envía al servidor ni identifica a nadie.
- **Formato:** un objeto JSON versionado bajo una clave única de la app, con try/catch para que la
  app funcione aunque el navegador bloquee el almacenamiento.
- **Límites, dichos en la app:** no se sincroniza entre dispositivos y se pierde si se borran los
  datos del sitio. Hay un botón **"Borrar mi progreso"**.
- **Mejora futura (no bloquea):** exportar/importar el progreso como archivo para llevarlo a otro
  dispositivo sin necesidad de cuentas.

---

## 9. Contenido semilla (lo que trae cargado el día 1)

- **Educación:** ~8–10 lecciones de los temas clave — qué es una acción, bonos, CEDEARs, fondos
  comunes de inversión, criptomonedas, el dólar y sus variantes, plazo fijo, inflación/IPC, UVA, PBI.
- **Glosario:** ~30–40 términos enlazados.
- **Quizzes:** uno por módulo inicial.

A partir de ahí se suma todo el contenido que se quiera desde el **admin**, sin programar.

---

## 10. UX y navegación

- **Home:** presenta "Aprender", un vistazo de "Mercado hoy" y un llamado a **empezar sin cuenta**
  (y a las Herramientas); accesos directos a los temas (cada tema con su color).
- **Aprender:** listado de temas → módulos → lecciones; glosario con buscador; quizzes.
- **Mercado hoy:** tarjetas con dólar y macro, con fecha de actualización.
- **Progreso:** sin panel personal ni login. Cada módulo/lección muestra su estado (vista, quiz
  hecho) leyendo el navegador; un "seguí donde dejaste" en la Home es opcional.
- **Diseño:** limpio, **colorido** (color por tema para orientar), legible, pensado para PC y
  adaptable a celular. Lenguaje llano; los términos técnicos enlazan al glosario. Modo claro/oscuro.

---

## 11. Despliegue y hosting

- Corre **local** (desarrollo, SQLite) y se prepara para **desplegar gratis** en la nube
  (Render / PythonAnywhere / Railway) con PostgreSQL.
- Configuración por **variables de entorno** (clave secreta, modo debug, base de datos), sin
  credenciales en el código.
- Archivos estáticos servidos de forma estándar para producción.

---

## 12. Seguridad y privacidad

- **Datos que se guardan:** **ninguno sobre las personas** en el servidor. No hay cuentas, email ni
  contraseñas. El progreso queda en el navegador de cada uno y se puede borrar desde la app.
- **Aviso de privacidad:** breve y claro: no se identifica a nadie; lo único que se guarda es el
  progreso, en el propio navegador.
- **Buenas prácticas base:** HTTPS en producción, protección CSRF (que Django trae), secretos fuera
  del repositorio.

---

## 13. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Una API de mercado cae o cambia | Dependencia aislada en `mercado`; caché + último valor conocido; fácil cambiar de proveedor. |
| Progreso solo en el navegador (se pierde al cambiar de dispositivo o borrar datos del sitio) | Se avisa en la app; exportar/importar el progreso queda como mejora futura. |
| Precisión del contenido financiero | Encuadre educativo; datos con fecha; aviso de "no es asesoramiento". |
| Que se interprete como asesoramiento regulado | Lenguaje informativo; sin recomendaciones personalizadas; avisos claros. |
| Que el proyecto crezca y se desordene | Apps con límites claros; funciones extra quedan para fases futuras. |

---

## 14. Criterios de éxito (Fase 1)

- Una persona puede **usar toda la app sin cuenta ni registro**, sin ningún tipo de acceso.
- Puede **leer una lección, hacer un quiz y ver su progreso**, guardado en su navegador.
- Puede **ver el dólar y la inflación/IPC del día** con su fecha.
- El responsable de la app **carga y edita contenido desde el admin** sin programar.
- El proyecto **arranca local** con pocos comandos y está **listo para desplegar**.

---

## 15. Fases futuras (registradas, se diseñan por separado)

- **Perfiles laborales ("qué me corresponde"):** catálogo por rubro (empleada doméstica,
  construcción, monotributo, etc.) con derechos/obligaciones según normativa vigente y fuentes.
- **"Salir de deudas" (escáner):** subida de captura/foto → OCR/IA → resumen de deudas → orientación
  para salir, con privacidad máxima (no guardar nada sensible).
- **Más mercado:** CEDEARs, letras (Lecaps) y la **serie histórica mensual de bonos** (fuente a definir).
- **Cuentas y sincronización del progreso entre dispositivos**, solo si alguna vez se decidiera dejar
  de ser 100 % abierta.

---

## 16. Decisiones abiertas (menores, no bloquean)

- Nombre comercial de la app (en la maqueta: "Plata Clara").
- Proveedor de hosting concreto (se elige al momento de publicar).
