"""
Uso manual, una sola vez (o cuando la sesion expire):
Abre un Chromium visible en la pantalla del usuario, navega al login de
Smartwifi QA, y espera a que el usuario resuelva el captcha e inicie sesion
a mano. Al presionar "Resume" en el inspector de Playwright, guarda
cookies + localStorage en auth_state.json para que el resto de scripts
reutilicen la sesion sin volver a pasar por el login/captcha.
"""
from playwright.sync_api import sync_playwright

LOGIN_URL = "https://qa.datawifi.co/easyfi/web/app.php/login"
STATE_PATH = "auth_state.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    # locale="es-ES": el sitio traduce automaticamente segun el idioma del
    # navegador (Weglot) -- sin esto puede arrancar en ingles.
    context = browser.new_context(locale="es-ES")
    page = context.new_page()
    page.goto(LOGIN_URL)

    print("Inicia sesion manualmente (usuario, contrasena, captcha).")
    print("Cuando veas el panel de administracion cargado, presiona 'Resume' en el inspector de Playwright.")
    page.pause()

    context.storage_state(path=STATE_PATH)
    print(f"Sesion guardada en {STATE_PATH}")

    browser.close()
