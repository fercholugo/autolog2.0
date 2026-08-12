@modulo:Contenido-Multimedia @submodulo:Videos
Feature: Gestion de videos en Contenido Multimedia

  @funcion:Ciclo-completo-CRUD
  Scenario: Ciclo completo de un video (crear, editar, activar/desactivar, eliminar)
    Given que el administrador esta en el listado de Videos
    When crea un nuevo video
    Then el video aparece en el listado
    When edita el nombre del video
    Then el listado muestra el nombre editado
    When desactiva el video
    Then el video queda desactivado
    When activa el video
    Then el video queda activado
    When elimina el video
    Then el video ya no aparece en el listado
