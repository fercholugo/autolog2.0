from src.abilities.browse_the_web import BrowseTheWeb


class ImagenEstaListada:
    def __init__(self, nombre):
        self.nombre = nombre

    def answered_by(self, actor):
        page = actor.ability_to(BrowseTheWeb).page
        buscador = page.locator("#tabla_imagenes_filter input[type='search']")
        buscador.fill(self.nombre)
        fila = page.locator("#tabla_imagenes tbody tr", has_text=self.nombre)
        try:
            fila.first.wait_for(state="visible", timeout=5000)
            return True
        except Exception:
            return False


class ImagenEstaActiva:
    def __init__(self, nombre):
        self.nombre = nombre

    def answered_by(self, actor):
        from src.utils.datatable import buscar_fila

        page = actor.ability_to(BrowseTheWeb).page
        # Recarga antes de leer: confirma el estado realmente persistido en
        # el servidor en vez de confiar en el DOM en memoria de la pagina.
        page.reload(wait_until="networkidle")
        fila = buscar_fila(page, "tabla_imagenes", self.nombre)
        return fila.locator("input.switch-input").is_checked()
