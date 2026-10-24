# App de Educación Financiera Pública — Diseño (Fase 1)

- **Fecha:** 2026-10-24
- **Estado:** Enfoque aprobado y acotado a educación financiera; pendiente go-ahead al plan de implementación.
- **Nombre de trabajo:** `finanzas-app` (el nombre comercial definitivo es cosmético y no bloquea nada).

---

## 1. Visión y objetivo

Una **app web gratuita de educación financiera** para el **público general de Argentina**, pensada
para gente **sin conocimientos previos**. Enseña, en lenguaje llano y desde cero, qué es y cómo
funciona cada instrumento y variable: acciones, criptomonedas, el dólar y sus variantes, plazo fijo,
fondos comunes de inversión (FCI), bonos, CEDEARs, e indicadores macro como **IPC, UVA y PBI**.

Uso **anónimo**, sin registro. Pensada para **PC** (con buena vista también en celular).

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
- La app **no accede a cuentas** bancarias ni de ningún organismo.

---

## 3. Alcance

### En alcance (Fase 1)

- **Educación financiera:** contenido organizado en Temas → Módulos → Lecciones, por nivel
  (principiante → intermedio → avanzado).
- **Glosario** buscable, con términos enlazados entre sí.
- **Quizzes** con puntaje y feedback, asociados a módulos.
- **Seguimiento de progreso sin cuentas:** guardado en el navegador (localStorage).
- **Datos de mercado en vivo (complemento del aprendizaje):** dólar (oficial/MEP/blue) + macro
  (IPC, UVA, inflación), con caché. *Refuerza lo aprendido mostrando números reales; es acotable
  si se lo quiere aún más mínimo.*
- **Panel de administración** para cargar/editar todo el contenido sin tocar código (Django admin).
- **Contenido semilla inicial** cargado.
- **Listo para desplegar gratis** en la nube.

### Fuera de alcance (futuro, a diseñar aparte)

- **Perfiles laborales** ("qué me corresponde" según normativa por rubro).
- **Escáner de deudas** (OCR/IA de documentos) y orientación para salir de deudas.
- **Acciones / Merval / CEDEARs** y **crypto** en vivo (diseñado para "sumar fácil" después).
- **Cuentas de usuario** y sincronización de progreso entre dispositivos.
- Multi-idioma (la app es en español).

---

## 4. Decisiones técnicas

| Decisión | Elección | Motivo |
|---|---|---|
| Lenguaje/Framework | **Python + Django** | Pedido del usuario (Python); Django trae ORM, migraciones y **admin automático** para cargar contenido sin código. |
| Base de datos | **SQLite** → **PostgreSQL** | SQLite para desarrollo (un archivo, cero config); Postgres al desplegar/crecer. El ORM de Django abstrae el cambio. |
| Frontend | **Plantillas server-side + JS liviano** | Simple, rápido, mantenible; no se justifica un SPA para contenido educativo. |
| Interactividad | JS puntual (quizzes, buscador del glosario) | Sin framework pesado de frontend. |
| Cuentas | **Ninguna** (anónimo) | Decisión del usuario; el progreso va al navegador. |
| Progreso | **localStorage** del navegador | Anónimo, sin backend de usuarios. Limitación asumida: por dispositivo. |
| Estilos | CSS propio liviano (o framework CSS mínimo) | Diseño limpio, sin dependencias pesadas. |

*Alternativas descartadas:* **FastAPI + React** (dos proyectos, sin admin gratis, overkill);
**Flask** (hay que construir a mano el admin que Django regala).

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
├── docs/              # esta especificación y futuras
└── manage.py
```

Responsabilidad de cada app:

- **`core`** — arma la home, las páginas institucionales y el aviso legal; sin lógica de negocio pesada.
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
- `Quiz` — título, descripción, módulo asociado (FK, opcional), publicado.
- `Pregunta` — quiz (FK), enunciado, explicación (feedback al responder), orden.
- `Opcion` — pregunta (FK), texto, `es_correcta` (bool).

**mercado**
- Sin tabla maestra. Usa el **framework de caché** de Django para guardar los últimos valores de las
  APIs con su timestamp. (Opcional a futuro: tabla de histórico, fuera de alcance.)

---

## 7. Datos de mercado en vivo (complemento)

- **Fuentes (Fase 1):** APIs públicas y gratuitas argentinas para **dólar** (oficial/MEP/blue) y
  **macro** (IPC, UVA, inflación). Candidatas: *dolarapi*, *ArgentinaDatos*, *BCRA Estadísticas*
  (se valida al implementar que estén vivas y sin clave).
- **Caché:** los valores se guardan unos minutos; toda la app lee de la caché, no pega a la API en
  cada visita.
- **Fallo de la API:** se muestra el **último valor conocido con su fecha**; si no hay previo, un
  aviso de "dato no disponible ahora". Nunca un error crudo.

---

## 8. Progreso sin cuentas (navegador)

- Se guarda en **localStorage**: lecciones leídas, módulos completados, quizzes aprobados y puntajes,
  y logros simples (p. ej. "completaste el nivel principiante").
- **Formato:** un objeto JSON versionado bajo una clave única de la app.
- **Limitaciones (comunicadas):** el progreso es **por dispositivo/navegador**; si borra los datos o
  cambia de PC, se pierde. Se avisa de forma clara.
- **Degradación elegante:** si el navegador bloquea el almacenamiento (modo privado), la app igual
  funciona; solo que no guarda el progreso.

---

## 9. Contenido semilla (lo que trae cargado el día 1)

- **Educación:** ~8–10 lecciones de los temas clave — qué es una acción, bonos, CEDEARs, fondos
  comunes de inversión, criptomonedas, el dólar y sus variantes, plazo fijo, inflación/IPC, UVA, PBI.
- **Glosario:** ~30–40 términos enlazados.
- **Quizzes:** uno por módulo inicial.

A partir de ahí se suma todo el contenido que se quiera desde el **admin**, sin programar.

---

## 10. UX y navegación

- **Home:** presenta "Aprender" y un vistazo de "Mercado hoy"; accesos directos a los temas.
- **Aprender:** listado de temas → módulos → lecciones; glosario con buscador; quizzes.
- **Mercado hoy:** tarjetas con dólar y macro, con fecha de actualización.
- **Diseño:** limpio y legible, pensado para PC y adaptable a celular. Lenguaje llano; cuando aparece
  un término técnico, se enlaza al glosario.

---

## 11. Despliegue y hosting

- Corre **local** (desarrollo, SQLite) y se prepara para **desplegar gratis** en la nube
  (Render / PythonAnywhere / Railway) con PostgreSQL.
- Configuración por **variables de entorno** (clave secreta, modo debug, base de datos), sin
  credenciales en el código.
- Archivos estáticos servidos de forma estándar para producción.

---

## 12. Seguridad y privacidad

- La app **no recolecta datos personales**. No hay cuentas; el progreso vive en el navegador.
- **Buenas prácticas base:** HTTPS en producción, protección CSRF (que Django trae), sin secretos en
  el repositorio.

---

## 13. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Una API de mercado cae o cambia | Dependencia aislada en `mercado`; caché + último valor conocido; fácil cambiar de proveedor. |
| Precisión del contenido financiero | Encuadre educativo; datos con fecha; aviso de "no es asesoramiento". |
| Que se interprete como asesoramiento regulado | Lenguaje informativo; sin recomendaciones personalizadas; avisos claros. |
| Que el proyecto crezca y se desordene | Apps con límites claros; funciones extra quedan para fases futuras. |

---

## 14. Criterios de éxito (Fase 1)

- Una persona sin conocimientos entra (sin registrarse), **lee una lección, hace un quiz y ve su
  progreso** guardado al volver.
- Puede **ver el dólar y la inflación/IPC del día** con su fecha.
- El responsable de la app **carga y edita contenido desde el admin** sin programar.
- El proyecto **arranca local** con pocos comandos y está **listo para desplegar**.

---

## 15. Fases futuras (registradas, se diseñan por separado)

- **Perfiles laborales ("qué me corresponde"):** catálogo por rubro (empleada doméstica,
  construcción, monotributo, etc.) con derechos/obligaciones según normativa vigente y fuentes.
- **"Salir de deudas" (escáner):** subida de captura/foto → OCR/IA → resumen de deudas → orientación
  para salir, con privacidad máxima (no guardar nada sensible).
- **Más mercado:** acciones/Merval/CEDEARs y crypto en vivo.
- **Cuentas opcionales** para sincronizar progreso entre dispositivos.

---

## 16. Decisiones abiertas (menores, no bloquean)

- Nombre comercial de la app (cosmético).
- Framework CSS mínimo vs. CSS propio (se define al implementar la UI).
- Proveedor de hosting concreto (se elige al momento de publicar).
