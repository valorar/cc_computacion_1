from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path("/Users/mag/Documents/hermes/cc_computacion_1")
REQUIRED_IDS = {"mision", "preparacion", "procedimiento", "comprobacion", "evaluacion", "apoyo"}


class Doc(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.h1 = 0
        self.title = ""
        self.in_title = False
        self.rubric_rows = 0
        self.in_rubric_body = False
        self.main = 0
        self.lang = None
        self.current = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html": self.lang = a.get("lang")
        if tag == "main": self.main += 1
        if tag == "h1": self.h1 += 1
        if tag == "title": self.in_title = True
        if a.get("id"): self.ids.append(a["id"])
        if a.get("aria-current"): self.current += 1
        for key in ("href", "src"):
            if a.get(key): self.refs.append(a[key])
        classes = (a.get("class") or "").split()
        if tag == "table" and "rubrica" in classes: self.in_rubric_body = True
        if tag == "tr" and self.in_rubric_body: self.rubric_rows += 1

    def handle_endtag(self, tag):
        if tag == "title": self.in_title = False
        if tag == "table" and self.in_rubric_body: self.in_rubric_body = False

    def handle_data(self, data):
        if self.in_title: self.title += data


def parse(path: Path) -> Doc:
    d = Doc(); d.feed(path.read_text(encoding="utf-8")); d.close(); return d


def main():
    all_pages = [ROOT / "index.html", ROOT / "programa.html"]
    all_pages += sorted(ROOT.glob("evaluacion_*/temas/tema_*.html"))
    practice_pages = []
    index_pages = []
    total_auto = total_manual = 0
    titles = []

    for ev in (1, 2, 3):
        folder = ROOT / f"evaluacion_{ev}" / "practicas"
        expected = [folder / f"practica_{n:02}.html" for n in range(1, 21)]
        actual = sorted(folder.glob("practica_*.html"))
        assert actual == expected, f"E{ev}: archivos no esperados o ausentes"
        index = folder / "index.html"
        assert index.exists(), f"E{ev}: falta índice"
        idx_text = index.read_text(encoding="utf-8")
        assert idx_text.count('class="tarjeta_practica"') == 20
        assert "15 autocorregibles" in idx_text and "5 corregidas con rúbrica" in idx_text
        for n, path in enumerate(expected, 1):
            text = path.read_text(encoding="utf-8")
            doc = parse(path)
            assert doc.lang == "es" and doc.main == 1 and doc.h1 == 1
            assert doc.current == 2, f"{path}: aria-current={doc.current}"
            assert len(doc.ids) == len(set(doc.ids)), f"{path}: ids duplicados"
            assert REQUIRED_IDS <= set(doc.ids), f"{path}: secciones ausentes"
            assert len(text) >= 6000, f"{path}: contenido breve"
            assert "Trabajo en el aula" in text and "55 min" in text
            assert "Categoría de nota" in text or "categoría Prácticas" in text
            assert "Prácticas (70%" in text or "Prácticas (70%" in text
            assert re.search(r"E%d_P%02d" % (ev, n), text)
            assert f"practica_{n:02}.html" in text
            if "Autocorregible en Moodle" in text:
                total_auto += 1
                assert "sin depender de complementos externos" in text
                assert "Moodle no inspecciona el archivo creado ni ejecuta programas" in text
                assert "La nota procede exclusivamente de respuestas objetivas" in text
                assert "respuestas ni claves" in text
                assert doc.rubric_rows == 0
            else:
                total_manual += 1
                assert n in {4, 8, 12, 16, 20}
                assert doc.rubric_rows == 5, (path, doc.rubric_rows)  # cabecera + 4 criterios
                for level in ("4 · Excelente", "3 · Adecuado", "2 · En proceso", "1 · Inicial"):
                    assert text.count(level) == 4, (path, level)
            titles.append(doc.title)
        practice_pages.extend(expected)
        index_pages.append(index)

    assert total_auto == 45 and total_manual == 15, (total_auto, total_manual)
    assert len(titles) == len(set(titles)) == 60
    all_pages += index_pages + practice_pages
    docs = {p.resolve(): parse(p) for p in all_pages}
    broken = []
    for page, doc in list(docs.items()):
        for ref in doc.refs:
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                continue
            target_text, _, fragment = ref.partition("#")
            target = (page.parent / target_text).resolve() if target_text else page
            if not target.exists():
                broken.append(f"{page.relative_to(ROOT)} -> {ref}")
                continue
            if fragment and target.suffix == ".html":
                target_doc = docs.get(target) or parse(target)
                if fragment not in target_doc.ids:
                    broken.append(f"{page.relative_to(ROOT)} -> ancla {ref}")
    assert not broken, "Enlaces rotos:\n" + "\n".join(broken)
    assert not any("-" in p.name for p in practice_pages)
    print(f"PRACTICES_AUDIT_OK pages={len(practice_pages)} indexes=3 auto={total_auto} manual={total_manual} rubrics=15 links=ok")


if __name__ == "__main__":
    main()
