"""
Carga la sesion guardada en auth_state.json (ver capture_login_state.py),
navega a una URL del admin de Smartwifi, y vuelca HTML + screenshot en
docs/mapping/<name>/ para su analisis (deteccion de elementos).

Uso:
    python scripts/capture_page.py <url> <name>

Ejemplo:
    python scripts/capture_page.py \
        https://qa.datawifi.co/easyfi/web/app.php/administrar/imagenes \
        imagenes
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

STATE_PATH = "auth_state.json"


def main(url: str, name: str) -> None:
    out_dir = Path("docs/mapping") / name
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=STATE_PATH)
        page = context.new_page()
        page.goto(url, wait_until="networkidle")

        (out_dir / "page.html").write_text(page.content(), encoding="utf-8")
        page.screenshot(path=str(out_dir / "page.png"), full_page=True)

        print(f"Volcado en {out_dir}/page.html y {out_dir}/page.png")
        print(f"URL final: {page.url}")

        browser.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python scripts/capture_page.py <url> <name>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
