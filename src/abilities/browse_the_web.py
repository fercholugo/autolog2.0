from src.utils.config import AUTH_STATE_PATH


class BrowseTheWeb:
    """Envuelve un BrowserContext/Page de Playwright ya autenticado."""

    def __init__(self, browser, context, page):
        self.browser = browser
        self.context = context
        self.page = page

    # Tamaño fijo para viewport y grabacion: sin esto, Playwright graba a su
    # resolucion por defecto (mas chica) y el video se ve borroso al maximizar.
    RESOLUCION = {"width": 1920, "height": 1080}

    @staticmethod
    def using_saved_session(playwright, storage_state=AUTH_STATE_PATH, headless=True, slow_mo=0, video_dir=None):
        browser = playwright.chromium.launch(headless=headless, slow_mo=slow_mo)
        context_args = {
            "storage_state": storage_state,
            "viewport": BrowseTheWeb.RESOLUCION,
            # El sitio traduce automaticamente segun el idioma del navegador
            # (Weglot); sin esto, Playwright a veces arranca en ingles y
            # todos los selectores por texto en espanol dejan de matchear.
            "locale": "es-ES",
        }
        if video_dir:
            context_args["record_video_dir"] = video_dir
            context_args["record_video_size"] = BrowseTheWeb.RESOLUCION
        context = browser.new_context(**context_args)
        page = context.new_page()
        return BrowseTheWeb(browser, context, page)

    def navigate_to(self, url):
        self.page.goto(url, wait_until="networkidle")

    def quit(self):
        self.context.close()
        self.browser.close()
