from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/Users/mag/Documents/hermes/cc_computacion_1")
BASE = "http://127.0.0.1:8765/"
PAGES = ["index.html", "programa.html"]
PAGES += [str(p.relative_to(ROOT)) for p in sorted(ROOT.glob("evaluacion_*/temas/tema_*.html"))]
PAGES += [str(p.relative_to(ROOT)) for p in sorted(ROOT.glob("evaluacion_*/practicas/*.html"))]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    for width, height in ((320, 780), (390, 844), (768, 900), (1280, 900)):
        page = b.new_page(viewport={"width": width, "height": height})
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        for relative in PAGES:
            response = page.goto(BASE + relative, wait_until="load")
            assert response and response.status == 200, (relative, response.status if response else None)
            assert page.locator("h1").count() == 1, relative
            assert page.locator("main").is_visible(), relative
            assert page.evaluate("innerWidth === document.documentElement.scrollWidth"), (relative, width, page.evaluate("[innerWidth, document.documentElement.scrollWidth]"))
        assert not errors, (width, errors[:10])
        page.close()
    context = b.new_context(java_script_enabled=False, viewport={"width": 375, "height": 844})
    page = context.new_page()
    for relative in PAGES:
        response = page.goto(BASE + relative, wait_until="load")
        assert response and response.status == 200, relative
        assert page.locator("main").is_visible(), relative
        assert page.locator("[data_navegacion]").is_visible(), relative
    context.close()
    b.close()
print(f"BROWSER_PRACTICES_OK pages={len(PAGES)} widths=4 no_js=yes")
