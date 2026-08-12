@modulo:Contenido-Multimedia @submodulo:Imagenes
Feature: Gestion de imagenes en Contenido Multimedia

  @funcion:Ciclo-completo-CRUD
  Scenario: Ciclo completo de una imagen (crear, editar, activar/desactivar, eliminar)
    Given que el administrador esta en el listado de Imagenes
    When crea una nueva imagen
    Then la imagen aparece en el listado
    When edita el nombre de la imagen
    Then el listado muestra el nombre editado
    When desactiva la imagen
    Then la imagen queda desactivada
    When activa la imagen
    Then la imagen queda activada
    When elimina la imagen
    Then la imagen ya no aparece en el listado
