# Contenido

Todo el contenido educativo vive acá, en JSON. No depende de la base de datos.

- `quiz.json`: cuestionario de nivel y umbrales de cada nivel.
- `modules/*.json`: un archivo por módulo, con sus lecciones y mini-tests.

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
