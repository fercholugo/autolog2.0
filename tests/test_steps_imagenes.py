import uuid

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.questions.imagen import ImagenEstaActiva, ImagenEstaListada
from src.tasks.gestionar_imagenes import (
    AbrirListadoDeImagenes,
    CambiarEstadoImagen,
    CrearImagen,
    EditarImagen,
    EliminarImagen,
)

scenarios("../features/imagenes.feature")

ARCHIVO_PRUEBA = "tests/fixtures/imagen_prueba.png"


@pytest.fixture
def datos():
    sufijo = uuid.uuid4().hex[:8]
    return {"nombre": f"qa_autolog_{sufijo}", "nombre_editado": f"qa_autolog_editada_{sufijo}"}


@given("que el administrador esta en el listado de Imagenes")
def ir_al_listado(actor):
    actor.attempts_to(AbrirListadoDeImagenes())


@when("crea una nueva imagen")
def crear_imagen(actor, datos):
    actor.attempts_to(
        CrearImagen(nombre=datos["nombre"], archivo=ARCHIVO_PRUEBA, descripcion="Imagen de prueba QA")
    )


@then("la imagen aparece en el listado")
def verificar_imagen_listada(actor, datos):
    assert actor.asks(ImagenEstaListada(datos["nombre"]))


@when("edita el nombre de la imagen")
def editar_imagen(actor, datos):
    actor.attempts_to(EditarImagen(nombre_actual=datos["nombre"], nuevo_nombre=datos["nombre_editado"]))


@then("el listado muestra el nombre editado")
def verificar_nombre_editado(actor, datos):
    assert actor.asks(ImagenEstaListada(datos["nombre_editado"]))


@when("desactiva la imagen")
def desactivar_imagen(actor, datos):
    actor.attempts_to(CambiarEstadoImagen(nombre=datos["nombre_editado"], activar=False))


@then("la imagen queda desactivada")
def verificar_desactivada(actor, datos):
    assert actor.asks(ImagenEstaActiva(datos["nombre_editado"])) is False


@when("activa la imagen")
def activar_imagen(actor, datos):
    actor.attempts_to(CambiarEstadoImagen(nombre=datos["nombre_editado"], activar=True))


@then("la imagen queda activada")
def verificar_activada(actor, datos):
    assert actor.asks(ImagenEstaActiva(datos["nombre_editado"])) is True


@when("elimina la imagen")
def eliminar_imagen(actor, datos):
    actor.attempts_to(EliminarImagen(nombre=datos["nombre_editado"]))


@then("la imagen ya no aparece en el listado")
def verificar_eliminada(actor, datos):
    assert actor.asks(ImagenEstaListada(datos["nombre_editado"])) is False
