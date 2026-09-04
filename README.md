# Ciencias de la Computación I

Sitio web de la asignatura **Ciencias de la Computación I**, 1.º de Bachillerato, curso 2026-2027.

## Estructura

- `assets/`: estilos, JavaScript, imágenes y documentos del sitio.
- `evaluacion_1/`, `evaluacion_2/`, `evaluacion_3/`: temas y prácticas de cada evaluación.
- `recursos/`: recursos comunes para el alumnado.

Cada carpeta `evaluacion_N/practicas/` contiene un índice y 20 prácticas obligatorias (`practica_01.html`…`practica_20.html`). Las carpetas `voluntarias/` quedan reservadas para ampliaciones futuras.

## Páginas disponibles

- `index.html`: portada y explicación breve de la forma de trabajo.
- `programa.html`: temporalización, bloques, temas, metodología y evaluación.
- `evaluacion_1/temas/`, `evaluacion_2/temas/` y `evaluacion_3/temas/`: páginas de los 16 temas del curso.
- `evaluacion_1/practicas/`, `evaluacion_2/practicas/` y `evaluacion_3/practicas/`: 60 páginas de prácticas más tres índices. En cada evaluación, 15 prácticas están diseñadas para corrección automática con tipos estándar de Moodle y 5 incluyen una rúbrica analítica para el profesor.

Los estilos comunes están en `assets/css/estilos.css` y la mejora progresiva de navegación en `assets/js/navegacion.js`. Las páginas funcionan sin dependencias externas y utilizan enlaces relativos.

La fuente estructurada de las prácticas está en `recursos/datos/practicas_eN.json`. `recursos/scripts/generar_practicas.py` regenera las 60 páginas y los tres índices; `auditar_practicas.py` y `auditar_navegador.py` comprueban recuentos, rúbricas, enlaces y comportamiento responsivo.

## Publicación y privacidad

El repositorio está preparado para alojar un sitio estático en GitHub Pages. No deben incluirse datos del alumnado, calificaciones, credenciales, soluciones, bancos de preguntas ni materiales restringidos al profesorado.

Los cuestionarios, las entregas y el libro de calificaciones se gestionarán en Moodle. Las 45 prácticas autocorregibles usan casos cerrados y tipos de pregunta estándar: Moodle califica las respuestas objetivas, no inspecciona archivos ni ejecuta programas. Los materiales de partida y las claves permanecen en Moodle, nunca en el sitio público.
