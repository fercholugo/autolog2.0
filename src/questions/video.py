from src.abilities.browse_the_web import BrowseTheWeb
from src.utils.datatable import buscar_fila

TABLA = "tabla_principal"


class VideoEstaListado:
    def __init__(self, nombre):
        self.nombre = nombre

    def answered_by(self, actor):
        page = actor.ability_to(BrowseTheWeb).page
        buscador = page.locator(f"#{TABLA}_filter input[type='search']")
        buscador.fill(self.nombre)
        fila = page.locator(f"#{TABLA} tbody tr", has_text=self.nombre)
        try:
            fila.first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False


class VideoEstaActivo:
    def __init__(self, nombre):
        self.nombre = nombre

    def answered_by(self, actor):
        page = actor.ability_to(BrowseTheWeb).page
        # Recarga antes de leer: confirma el estado realmente persistido en
        # el servidor en vez de confiar en el DOM en memoria de la pagina.
        page.reload(wait_until="networkidle")
        fila = buscar_fila(page, TABLA, self.nombre)
        return fila.locator("input.switch-input").is_checked()
