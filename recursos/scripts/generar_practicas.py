from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path("/Users/mag/Documents/hermes/cc_computacion_1")
THEME_TITLES = {
    1: "Ideas que hicieron posible la computación",
    2: "Cómo funciona un ordenador",
    3: "Por dentro: componentes, conexiones y arranque",
    4: "El sistema operativo y los archivos",
    5: "Lenguajes, aplicaciones y utilidades",
    6: "Documentos que comunican",
    7: "Hojas de cálculo: datos que responden",
    8: "Bases de datos: ordenar para consultar",
    9: "Presentar y coordinar un proyecto",
    10: "La web como documento público",
    11: "Internet: evolución, servicios y riesgos",
    12: "Python: datos, expresiones y conversación",
    13: "Tomar decisiones y repetir",
    14: "Colecciones para trabajar con muchos datos",
    15: "Funciones, pruebas y depuración",
    16: "Proyecto de integración en Python",
}
EXPECTED_THEMES = {1: range(1, 6), 2: range(6, 12), 3: range(12, 17)}
SESSION_RANGES = {1: (38, 42), 2: (34, 38), 3: (26, 30)}
MANUAL_NUMBERS = {4, 8, 12, 16, 20}


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def ul(items: list[str], class_name: str = "") -> str:
    c = f' class="{e(class_name)}"' if class_name else ""
    return f"<ul{c}>" + "".join(f"<li>{e(item)}</li>" for item in items) + "</ul>"


def ol(items: list[str]) -> str:
    return "<ol class=\"pasos_practica\">" + "".join(f"<li>{e(item)}</li>" for item in items) + "</ol>"


def validate(evaluation: int, items: list[dict]) -> None:
    assert len(items) == 20, (evaluation, len(items))
    assert [x["numero"] for x in items] == list(range(1, 21))
    autos = [x for x in items if x["modalidad"] == "autocorregible_moodle"]
    manuals = [x for x in items if x["modalidad"] == "rubrica_docente"]
    assert len(autos) == 15 and len(manuals) == 5
    assert {x["numero"] for x in manuals} == MANUAL_NUMBERS
    low, high = SESSION_RANGES[evaluation]
    total = sum(x["sesiones"] for x in items)
    assert low <= total <= high, (evaluation, total)
    covered = set()
    titles = set()
    for x in items:
        assert x["titulo"] not in titles
        titles.add(x["titulo"])
        assert x["sesiones"] >= 1
        assert 5 <= len(x["pasos"]) <= 8
        assert 4 <= len(x["comprobaciones"]) <= 6
        assert set(x["tema_numeros"]).issubset(set(EXPECTED_THEMES[evaluation]))
        covered.update(x["tema_numeros"])
        if x["modalidad"] == "rubrica_docente":
            assert x["moodle"] is None
            assert len(x["rubrica"]) == 4
            assert sum(c["peso"] for c in x["rubrica"]) == 100
            for c in x["rubrica"]:
                assert set(c["niveles"]) == {"1", "2", "3", "4"}
        else:
            assert x["rubrica"] == []
            assert x["moodle"] is not None
            assert 6 <= x["moodle"]["numero_items"] <= 12
    assert covered == set(EXPECTED_THEMES[evaluation]), (evaluation, covered)


def common_head(title: str, description: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{e(description)}">
  <title>{e(title)}</title>
  <meta name="theme-color" content="#f4f0e6">
  <link rel="icon" href="../../assets/img/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../../assets/css/estilos.css">
  <script src="../../assets/js/navegacion.js" defer></script>
</head>'''


def header(evaluation: int, current: str) -> str:
    if current == "index.html":
        practice_links = f'<li><a href="index.html" aria-current="page">Prácticas E{evaluation}</a></li>'
    else:
        practice_links = f'<li><a href="index.html">Prácticas E{evaluation}</a></li><li><a href="{e(current)}" aria-current="page">Práctica</a></li>'
    return f'''<a class="saltar" href="#contenido">Saltar al contenido</a>
<div class="barra_progreso" aria-hidden="true"><span data_progreso></span></div>
<header class="cabecera"><div class="cabecera_interior">
  <a class="marca" href="../../index.html" aria-label="Inicio de Ciencias de la Computación I"><span class="marca_codigo">CC1</span><span>Ciencias de la Computación I<small>1.º Bachillerato · 2026–2027</small></span></a>
  <button class="boton_menu" type="button" aria-expanded="false" aria-controls="navegacion_principal" data_boton_menu>Menú</button>
  <nav class="navegacion" id="navegacion_principal" aria-label="Navegación principal" data_navegacion><ul>
    <li><a href="../../index.html">Inicio</a></li><li><a href="../../programa.html">Programa</a></li>{practice_links}
  </ul></nav>
</div></header>'''


def render_rubric(item: dict) -> str:
    rows = []
    for c in item["rubrica"]:
        n = c["niveles"]
        rows.append(f'''<tr><th scope="row">{e(c['criterio'])}<small>{e(c['peso'])}%</small></th><td><strong>4 · Excelente</strong><br>{e(n['4'])}</td><td><strong>3 · Adecuado</strong><br>{e(n['3'])}</td><td><strong>2 · En proceso</strong><br>{e(n['2'])}</td><td><strong>1 · Inicial</strong><br>{e(n['1'])}</td></tr>''')
    return '''<p>El profesor aplica esta rúbrica al producto entregado. La puntuación ponderada se transforma a una nota sobre 10 dentro de la categoría Prácticas (70% de la evaluación).</p><p class="ayuda_desplazamiento">En pantallas pequeñas, desplaza la tabla lateralmente para consultar los cuatro niveles.</p><section class="tabla_responsiva tabla_rubrica" aria-label="Rúbrica desplazable" tabindex="0"><table class="rubrica"><thead><tr><th scope="col">Criterio y peso</th><th scope="col">4</th><th scope="col">3</th><th scope="col">2</th><th scope="col">1</th></tr></thead><tbody>''' + "".join(rows) + "</tbody></table></section>"


def moodle_type(value: str) -> str:
    mapping = {
        "opcion_multiple": "opción múltiple",
        "numerica": "numérica",
        "arrastrar_soltar": "arrastrar y soltar",
        "respuesta_corta_con_variantes": "respuesta corta con variantes",
        "arrastrar/soltar": "arrastrar y soltar",
    }
    return mapping.get(value.lower(), value)


def render_moodle(item: dict) -> str:
    m = item["moodle"]
    types = ", ".join(moodle_type(value) for value in m["tipos_pregunta"])
    return f'''<p>{e(m['actividad'])}</p>
<div class="aviso"><strong>Protocolo de autocorrección</strong><p>Al abrir la actividad, Moodle entrega un caso cerrado con datos, nombres, identificadores y parámetros fijados. La nota procede exclusivamente de respuestas objetivas derivadas de ese caso. Moodle no inspecciona el archivo creado ni ejecuta programas: el artefacto se conserva como cuaderno de trabajo y no requiere corrección docente.</p></div>
<dl class="ficha_evaluacion"><dt>Cómo se corrige</dt><dd>Automáticamente en Moodle, sin depender de complementos externos.</dd><dt>Categoría de nota</dt><dd>Prácticas (70% de la evaluación); no forma parte de los cuestionarios teóricos del 30%.</dd><dt>Preguntas</dt><dd>{e(m['numero_items'])} ítems: {e(types)}.</dd><dt>Intentos</dt><dd>{e(m['intentos'])}</dd><dt>Calificación</dt><dd>{e(m['calificacion'])}</dd><dt>Evidencia</dt><dd>{e(m['evidencia'])}</dd><dt>Retroalimentación</dt><dd>{e(m['retroalimentacion'])}</dd></dl>
<div class="aviso"><strong>Importante</strong><p>La página pública no contiene respuestas ni claves. La actividad y su retroalimentación se alojarán dentro del aula Moodle.</p></div>'''


def render_page(evaluation: int, item: dict) -> str:
    n = item["numero"]
    filename = f"practica_{n:02}.html"
    label = "Autocorregible en Moodle" if item["modalidad"] == "autocorregible_moodle" else "Corrección mediante rúbrica"
    badge = "modalidad_auto" if item["modalidad"] == "autocorregible_moodle" else "modalidad_docente"
    links = "".join(
        f'<li><a href="../temas/tema_{a["tema"]:02}.html">Tema {a["tema"]}: {e(THEME_TITLES[a["tema"]])}</a><br><small>{e(a["seccion"])}</small></li>'
        for a in item["apoyo_teorico"]
    )
    prev_link = '<a href="index.html">← Índice de prácticas</a>' if n == 1 else f'<a href="practica_{n-1:02}.html">← Práctica {n-1:02}</a>'
    next_link = '<a href="index.html">Volver al índice →</a>' if n == 20 else f'<a href="practica_{n+1:02}.html">Práctica {n+1:02} →</a>'
    evaluation_html = render_moodle(item) if item["modalidad"] == "autocorregible_moodle" else render_rubric(item)
    if item["modalidad"] == "autocorregible_moodle":
        delivery = f"Completa la actividad autocorregible de Moodle y conserva {item['archivo']} en tu carpeta de trabajo hasta cerrar la evaluación. No se sube para corrección manual."
    else:
        delivery = item["entrega"]
    page_title = f"E{evaluation} · P{n:02}: {item['titulo']}"
    if len(page_title) > 68:
        page_title = page_title[:67].rstrip(" ,:;–-") + "…"
    return common_head(page_title, f"Práctica {n:02} de la {evaluation}.ª evaluación: {item['titulo']}") + f'''
<body>
{header(evaluation, filename)}
<main id="contenido">
  <nav class="migas contenedor" aria-label="Migas de pan"><ol><li><a href="../../index.html">Inicio</a></li><li><a href="../../programa.html#evaluacion_{evaluation}">{evaluation}.ª evaluación</a></li><li><a href="index.html">Prácticas</a></li><li aria-current="page">Práctica {n:02}</li></ol></nav>
  <section class="hero hero_tema hero_practica"><div class="contenedor hero_rejilla"><div>
    <p class="etiqueta">E{evaluation}_P{n:02} · {e(label)}</p><h1>{e(item['titulo'])}</h1><p class="hero_intro">{e(item['reto'])}</p>
    <ul class="meta_tema" aria-label="Datos de la práctica"><li>{e(item['sesiones'])} {'sesión' if item['sesiones'] == 1 else 'sesiones'} de 55 min</li><li>{e(item['agrupamiento'])}</li><li>{e(label)}</li><li>Trabajo en el aula</li></ul>
  </div><aside class="hero_lateral" aria-label="Producto de la práctica {n:02}"><p><strong>Producto</strong><br>{e(item['producto'])}</p><p><strong>Archivo</strong><br><code>{e(item['archivo'])}</code></p></aside></div></section>
  <section class="seccion"><div class="contenedor rejilla_tema">
    <nav class="indice_lateral" aria-label="Índice de la práctica"><strong>En esta página</strong><ol><li><a href="#mision">Misión</a></li><li><a href="#preparacion">Preparación</a></li><li><a href="#procedimiento">Procedimiento</a></li><li><a href="#comprobacion">Comprobación</a></li><li><a href="#evaluacion">Evaluación</a></li><li><a href="#apoyo">Apoyo teórico</a></li></ol></nav>
    <article class="articulo_tema articulo_practica">
      <section id="mision"><span class="etiqueta">01 / MISIÓN</span><h2>El encargo</h2><p>{e(item['relato'])}</p><div class="aviso"><strong>Reto</strong><p>{e(item['reto'])}</p></div><dl class="ficha_evaluacion"><dt>Entrega</dt><dd>{e(delivery)}</dd><dt>Nombre</dt><dd><code>{e(item['archivo'])}</code></dd><dt>Modalidad</dt><dd><span class="pildora {badge}">{e(label)}</span></dd></dl></section>
      <section id="preparacion"><span class="etiqueta">02 / ANTES DE EMPEZAR</span><h2>Prepara el puesto</h2>{ul(item['preparacion'], 'lista_comprobacion')}<p class="nota"><strong>Material de partida:</strong> los archivos, fichas, datos o casos citados se publican adjuntos a la actividad Moodle correspondiente. En las autocorregibles pertenecen a la variante cerrada asignada y no deben sustituirse por datos propios.</p></section>
      <section id="procedimiento"><span class="etiqueta">03 / CONSTRUIR</span><h2>Procedimiento de trabajo</h2>{ol(item['pasos'])}<p class="nota"><strong>Gestión del tiempo:</strong> reserva los últimos diez minutos para nombrar, guardar y comprobar la entrega. El trabajo evaluable se termina en el aula.</p></section>
      <section id="comprobacion"><span class="etiqueta">04 / VERIFICAR</span><h2>Antes de entregar</h2>{ul(item['comprobaciones'], 'lista_comprobacion')}<div class="columnas_dos"><div><h3>Accesibilidad</h3><p>{e(item['accesibilidad'])}</p></div><div><h3>Privacidad</h3><p>{e(item['privacidad'])}</p></div></div></section>
      <section id="evaluacion"><span class="etiqueta">05 / EVALUACIÓN</span><h2>{e(label)}</h2>{evaluation_html}</section>
      <section id="apoyo"><span class="etiqueta">06 / CONSULTA</span><h2>Apoyo teórico</h2><p>Consulta únicamente los apartados necesarios para desbloquear el siguiente paso.</p><ul class="enlaces_teoria">{links}</ul></section>
    </article>
  </div></section>
</main>
<footer class="pie"><div class="contenedor pie_interior"><p><strong>E{evaluation} · Práctica {n:02}</strong><br><small>{e(label)} · {e(item['sesiones'])} sesiones</small></p><p>{prev_link} · {next_link}<br><small><a href="index.html">20 prácticas de la evaluación</a> · <a href="../../programa.html#evaluacion_{evaluation}">Programa</a></small></p></div></footer>
</body></html>
'''


def render_index(evaluation: int, items: list[dict]) -> str:
    total = sum(x["sesiones"] for x in items)
    cards = []
    for item in items:
        n = item["numero"]
        auto = item["modalidad"] == "autocorregible_moodle"
        label = "Moodle autocorrige" if auto else "Rúbrica docente"
        klass = "modalidad_auto" if auto else "modalidad_docente"
        temas = ", ".join(f"T{x:02}" for x in item["tema_numeros"])
        cards.append(f'''<li class="tarjeta_practica"><a href="practica_{n:02}.html"><span class="practica_numero">E{evaluation}_P{n:02}</span><h2>{e(item['titulo'])}</h2></a><p>{e(item['reto'])}</p><ul class="meta_tema"><li>{e(item['sesiones'])} {'sesión' if item['sesiones']==1 else 'sesiones'}</li><li>{e(temas)}</li><li class="{klass}">{e(label)}</li></ul></li>''')
    return common_head(f"Prácticas de la {evaluation}.ª evaluación", f"Veinte prácticas de la {evaluation}.ª evaluación de Ciencias de la Computación I.") + f'''
<body>
{header(evaluation, 'index.html')}
<main id="contenido">
  <nav class="migas contenedor" aria-label="Migas de pan"><ol><li><a href="../../index.html">Inicio</a></li><li><a href="../../programa.html#evaluacion_{evaluation}">{evaluation}.ª evaluación</a></li><li aria-current="page">Prácticas</li></ol></nav>
  <section class="hero hero_programa"><div class="contenedor hero_rejilla"><div><p class="etiqueta">{evaluation}.ª evaluación · Aprender haciendo</p><h1>20 prácticas para construir y comprobar</h1><p class="hero_intro">Quince generan una calificación automática en Moodle después de trabajar con un artefacto real; cinco producen trabajos ricos que el profesor valora con una rúbrica pública.</p></div><aside class="hero_lateral" aria-label="Distribución de prácticas"><p><strong>Plan de aula</strong></p><ul><li>{total} sesiones prácticas de 55 minutos.</li><li>15 autocorregibles en Moodle.</li><li>5 corregidas con rúbrica.</li><li>Todo se realiza en el aula.</li></ul></aside></div></section>
  <section class="franja_datos" aria-label="Distribución orientativa del tiempo"><ul class="contenedor lista_datos"><li><strong>Práctica</strong><span>75% del tiempo</span></li><li><strong>Explicación</strong><span>20% del tiempo</span></li><li><strong>Tests</strong><span>5% del tiempo</span></li><li><strong>Corrección manual</strong><span>5 de 20 trabajos</span></li></ul></section>
  <section class="seccion"><div class="contenedor"><div class="encabezado_seccion"><span class="numero_seccion">01 / RECORRIDO</span><div><h2>Prácticas de la evaluación</h2><p class="subtitulo">El orden construye capacidades progresivamente. Cada página indica la entrega, el tiempo, las comprobaciones y el mecanismo de evaluación.</p></div></div><ol class="rejilla_practicas">{''.join(cards)}</ol></div></section>
  <section class="seccion"><div class="contenedor columnas_dos"><div><h2>Qué significa «autocorregible»</h2><p>Antes de responder, se crea, ejecuta o inspecciona un producto en el ordenador. Moodle asigna un caso cerrado y comprueba respuestas objetivas derivadas de ese trabajo mediante <a href="https://docs.moodle.org/500/en/Question_types">tipos de pregunta estándar</a>; no inspecciona el archivo ni ejecuta programas. Estas notas se guardan en la categoría Prácticas (70%), separada de los cuestionarios teóricos (30%).</p></div><div><h2>Qué corrige el profesor</h2><p>Los productos complejos se valoran con cuatro criterios ponderados y cuatro niveles observables. La <a href="https://docs.moodle.org/500/en/Rubrics">rúbrica de Moodle</a> aparece completa en la página de la práctica antes de empezar.</p></div></div></section>
</main>
<footer class="pie"><div class="contenedor pie_interior"><p><strong>Prácticas · {evaluation}.ª evaluación</strong><br><small>20 actividades · {total} sesiones</small></p><p><a href="../../programa.html#evaluacion_{evaluation}">Programa</a> · <a href="../../index.html">Inicio</a><br><small>Sitio público sin soluciones ni datos personales.</small></p></div></footer>
</body></html>
'''


def main() -> None:
    for evaluation in (1, 2, 3):
        src = ROOT / "recursos" / "datos" / f"practicas_e{evaluation}.json"
        items = json.loads(src.read_text(encoding="utf-8"))
        validate(evaluation, items)
        folder = ROOT / f"evaluacion_{evaluation}" / "practicas"
        folder.mkdir(parents=True, exist_ok=True)
        for item in items:
            (folder / f"practica_{item['numero']:02}.html").write_text(render_page(evaluation, item), encoding="utf-8")
        (folder / "index.html").write_text(render_index(evaluation, items), encoding="utf-8")
        print(f"E{evaluation}: pages=20 auto=15 manual=5 sessions={sum(x['sesiones'] for x in items)}")


if __name__ == "__main__":
    main()
