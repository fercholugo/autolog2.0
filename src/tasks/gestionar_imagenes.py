from src.abilities.browse_the_web import BrowseTheWeb
from src.utils.config import BASE_URL
from src.utils.datatable import abrir_menu_administrar, buscar_fila

IMAGENES_URL = f"{BASE_URL}/administrar/imagenes"


class AbrirListadoDeImagenes:
    def perform_as(self, actor):
        actor.ability_to(BrowseTheWeb).navigate_to(IMAGENES_URL)


class CrearImagen:
    def __init__(self, nombre, archivo, descripcion="", destino=""):
        self.nombre = nombre
        self.archivo = archivo
        self.descripcion = descripcion
        self.destino = destino

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        page.get_by_role("button", name="Agregar imagen").click()
        formulario = page.frame_locator("#fragmento")
        formulario.locator("#product_nombre").fill(self.nombre)
        if self.descripcion:
            formulario.locator("#product_descripcion").fill(self.descripcion)
        if self.destino:
            formulario.locator("#product_destino").fill(self.destino)
        # Requerido por la validacion del boton "Guardar" aunque el HTML no
        # lo marque `required`: sin archivo tira "Por favor llene los campos
        # minimos" y no guarda nada.
        formulario.locator("#product_ruta").set_input_files(self.archivo)

        # El boton "Guardar" del modal vive fuera del iframe: lee los campos
        # de adentro por JS y dispara el submit oculto del formulario real.
        page.locator("#guardar").click()
        page.wait_for_load_state("networkidle")


class EditarImagen:
    def __init__(self, nombre_actual, nuevo_nombre=None, nueva_descripcion=None, nuevo_destino=None):
        self.nombre_actual = nombre_actual
        self.nuevo_nombre = nuevo_nombre
        self.nueva_descripcion = nueva_descripcion
        self.nuevo_destino = nuevo_destino

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        fila = buscar_fila(page, "tabla_imagenes", self.nombre_actual)
        abrir_menu_administrar(fila)
        fila.get_by_role("link", name="Editar").click()

        modal = page.locator("#editarimagen")
        if self.nuevo_nombre is not None:
            modal.locator("#nuevo_nombre").fill(self.nuevo_nombre)
        if self.nueva_descripcion is not None:
            modal.locator("#nueva_descripcion").fill(self.nueva_descripcion)
        if self.nuevo_destino is not None:
            modal.locator("#nuevo_destino").fill(self.nuevo_destino)

        modal.locator("#guardaredicion").click()
        page.wait_for_load_state("networkidle")


class CambiarEstadoImagen:
    """activar=True enciende el switch, activar=False lo apaga.

    El <span> decorativo del switch intercepta los clics reales sobre el
    <input> (confirmado: Playwright reporta "intercepts pointer events" con
    click normal, force=True y hasta el .click() nativo via evaluate no
    togglean el checkbox de forma confiable). En vez de pelear con el click,
    disparamos el mismo evento 'change' que dispara el navegador tras un
    click exitoso -> ejecuta el onchange="bloquear(...)" real de la pagina,
    y esperamos la respuesta real del endpoint para confirmar que el cambio
    quedo persistido en el servidor antes de seguir.
    """

    def __init__(self, nombre, activar):
        self.nombre = nombre
        self.activar = activar

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        fila = buscar_fila(page, "tabla_imagenes", self.nombre)
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


class EliminarImagen:
    def __init__(self, nombre):
        self.nombre = nombre

    def perform_as(self, actor):
        page = actor.ability_to(BrowseTheWeb).page

        fila = buscar_fila(page, "tabla_imagenes", self.nombre)
        abrir_menu_administrar(fila)
        fila.get_by_role("link", name="Eliminar").click()

        # El popup de confirmacion (SweetAlert2) tiene animacion de entrada;
        # clickear "Aceptar" apenas es detectable como visible puede caer
        # durante la transicion y no registrar el click.
        boton_aceptar = page.get_by_role("button", name="Aceptar")
        boton_aceptar.wait_for(state="visible")
        page.wait_for_timeout(500)

        with page.expect_response("**/eliminar_elemento**"):
            boton_aceptar.click()
        page.wait_for_load_state("networkidle")
