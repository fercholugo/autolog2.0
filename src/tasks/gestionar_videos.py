from src.abilities.browse_the_web import BrowseTheWeb
from src.utils.config import BASE_URL
from src.utils.datatable import abrir_menu_administrar, buscar_fila

VIDEOS_URL = f"{BASE_URL}/administrar/videos"
TABLA = "tabla_principal"  # ojo: a diferencia de Imagenes, NO se llama "tabla_videos"


class AbrirListadoDeVideos:
    def perform_as(self, actor):
        actor.ability_to(BrowseTheWeb).navigate_to(VIDEOS_URL)


class CrearVideo:
    def __init__(self, nombre, url, descripcion="", imagen_respaldo=None, verticalizar=None):
        self.nombre = nombre
        self.url = url
        self.descripcion = descripcion
        self.imagen_respaldo = imagen_respaldo
        self.verticalizar = verticalizar

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        page.get_by_role("button", name="Agregar video").click()
        modal = page.locator("#agregarvideo")
        modal.locator("#nombre_video").fill(self.nombre)
        if self.descripcion:
            modal.locator("#descripcion_video").fill(self.descripcion)
        modal.locator("#url_video").fill(self.url)
        if self.imagen_respaldo:
            modal.locator("#imagen_respaldo").select_option(label=self.imagen_respaldo)
        if self.verticalizar is not None:
            modal.locator("#verticalizar_nuevo").select_option("1" if self.verticalizar else "0")

        # A diferencia de Imagenes, este modal NO tiene iframe: el boton
        # "Guardar" envia directo por POST, sin trucos de frame. Esperamos
        # la respuesta real del POST antes de seguir (un simple "networkidle"
        # puede resolver antes de que el location.reload() posterior corra).
        with page.expect_response("**/guardar_contenido**"):
            modal.locator("#guardar").click()
        page.wait_for_load_state("networkidle")


class EditarVideo:
    def __init__(self, nombre_actual, nuevo_nombre=None, nueva_descripcion=None, nueva_url=None):
        self.nombre_actual = nombre_actual
        self.nuevo_nombre = nuevo_nombre
        self.nueva_descripcion = nueva_descripcion
        self.nueva_url = nueva_url

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        fila = buscar_fila(page, TABLA, self.nombre_actual)
        abrir_menu_administrar(fila)
        fila.get_by_role("link", name="Editar").click()

        modal = page.locator("#editarvideo")
        if self.nuevo_nombre is not None:
            modal.locator("#nuevo_nombre").fill(self.nuevo_nombre)
        if self.nueva_descripcion is not None:
            modal.locator("#nueva_descripcion").fill(self.nueva_descripcion)
        if self.nueva_url is not None:
            modal.locator("#nueva_url").fill(self.nueva_url)

        with page.expect_response("**/editar_contenido**"):
            modal.locator("#guardaredicion").click()
        page.wait_for_load_state("networkidle")


class CambiarEstadoVideo:
    """Mismo defecto de accesibilidad que en Imagenes: el <span> decorativo
    del switch tapa al <input> real. Se dispara el evento 'change' por JS
    en vez de clickear, y se espera la respuesta real del servidor."""

    def __init__(self, nombre, activar):
        self.nombre = nombre
        self.activar = activar

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        fila = buscar_fila(page, TABLA, self.nombre)
        switch = fila.locator("input.switch-input")
        if switch.is_checked() == self.activar:
            return

        with page.expect_response("**/cambiar_estado_contenido**"):
            switch.evaluate(
                """
                (el, activar) => {
                    el.checked = activar;
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                }
                """,
                self.activar,
            )


class EliminarVideo:
    def __init__(self, nombre):
        self.nombre = nombre

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        fila = buscar_fila(page, TABLA, self.nombre)
        abrir_menu_administrar(fila)
        fila.get_by_role("link", name="Eliminar").click()

        # Mismo popup SweetAlert2 con animacion de entrada que en Imagenes.
        boton_aceptar = page.get_by_role("button", name="Aceptar")
        boton_aceptar.wait_for(state="visible")
        page.wait_for_timeout(500)

        with page.expect_response("**/eliminar_elemento**"):
            boton_aceptar.click()
        page.wait_for_load_state("networkidle")
