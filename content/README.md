# Contenido

Todo el contenido educativo vive acá, en JSON. No depende de la base de datos.

- `quiz.json`: cuestionario de nivel y umbrales de cada nivel.
- `modules/*.json`: un archivo por módulo, con sus lecciones y mini-tests.
- `glosario.json`: términos del glosario con categoría y enlaces entre sí (semilla del Batch 1).
- `ruta.json`: los 5 pasos de la "Ruta" (mapa pedagógico ordenado, semilla del Batch 1).

## Reglas de calidad

- Cada afirmación factual se revisa contra una fuente oficial (BCRA, CNV, INDEC) y se anota en `sources`.
- Los archivos incluidos son **ejemplos**: reemplazarlos por contenido revisado.
- Lenguaje claro y sin jerga. Si hay un término técnico, se explica en la misma lección.
- El contenido es educativo. No recomienda activos concretos.

## Campos

**Pregunta del cuestionario**: `id`, `dimension` (`conocimiento`, `comportamiento` o `actitud`),
`topic`, `text`, `options`, `correct`, `explanation`, `points`.

**Módulo**: `id`, `order`, `title`, `goals`, `minLevel`, `macroSeries`, `lessons`.

**Lección**: `id`, `title`, `summary`, `body` (markdown), `sources`, `miniTest`.

**Término (`glosario.json`)**: `slug`, `termino`, `categoria` (id de `categorias`), `definicion`,
`ejemplo`, `relacionados` (lista de slugs de otros términos), `publicado`. Mapea al modelo `Termino`
de la app `glosario`.

**Paso de la ruta (`ruta.json`)**: `order`, `slug`, `icon` (nombre de ícono lucide), `title`,
`body`, `tip`, `herramienta` (clave de la herramienta asociada en `/herramientas`).
