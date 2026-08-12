import uuid

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from src.questions.video import VideoEstaActivo, VideoEstaListado
from src.tasks.gestionar_videos import (
    AbrirListadoDeVideos,
    CambiarEstadoVideo,
    CrearVideo,
    EditarVideo,
    EliminarVideo,
)

scenarios("../features/videos.feature")

URL_VIDEO_PRUEBA = "http://www.w3schools.com/html/mov_bbb.mp4"


@pytest.fixture
def datos():
    sufijo = uuid.uuid4().hex[:8]
    return {"nombre": f"qa_autolog_video_{sufijo}", "nombre_editado": f"qa_autolog_video_editado_{sufijo}"}


@given("que el administrador esta en el listado de Videos")
def ir_al_listado(actor):
    actor.attempts_to(AbrirListadoDeVideos())


@when("crea un nuevo video")
def crear_video(actor, datos):
    actor.attempts_to(
        CrearVideo(nombre=datos["nombre"], url=URL_VIDEO_PRUEBA, descripcion="Video de prueba QA")
    )


@then("el video aparece en el listado")
def verificar_video_listado(actor, datos):
    assert actor.asks(VideoEstaListado(datos["nombre"]))


@when("edita el nombre del video")
def editar_video(actor, datos):
    actor.attempts_to(EditarVideo(nombre_actual=datos["nombre"], nuevo_nombre=datos["nombre_editado"]))


@then("el listado muestra el nombre editado")
def verificar_nombre_editado(actor, datos):
    assert actor.asks(VideoEstaListado(datos["nombre_editado"]))


@when("desactiva el video")
def desactivar_video(actor, datos):
    actor.attempts_to(CambiarEstadoVideo(nombre=datos["nombre_editado"], activar=False))


@then("el video queda desactivado")
def verificar_desactivado(actor, datos):
    assert actor.asks(VideoEstaActivo(datos["nombre_editado"])) is False


@when("activa el video")
def activar_video(actor, datos):
    actor.attempts_to(CambiarEstadoVideo(nombre=datos["nombre_editado"], activar=True))


@then("el video queda activado")
def verificar_activado(actor, datos):
    assert actor.asks(VideoEstaActivo(datos["nombre_editado"])) is True


@when("elimina el video")
def eliminar_video(actor, datos):
    actor.attempts_to(EliminarVideo(nombre=datos["nombre_editado"]))


@then("el video ya no aparece en el listado")
def verificar_eliminado(actor, datos):
    assert actor.asks(VideoEstaListado(datos["nombre_editado"])) is False
