# Mapeo — CREA > Contenido multimedia > Videos

URL listado: `https://qa.datawifi.co/easyfi/web/app.php/administrar/videos`

## Comparación rápida con Imágenes

Comparte la misma arquitectura de fondo (Symfony + jQuery + DataTables +
switch con el mismo defecto de accesibilidad + confirmación SweetAlert2 con
animación + borrado con validación de dependencias). Lo que cambia:

| | Imágenes | Videos |
|---|---|---|
| Id de la tabla | `tabla_imagenes` | **`tabla_principal`** (¡ojo, no es `tabla_videos`!) |
| Crear | Modal con **iframe** a `/subir_imagen` | **Sin iframe** — campos directos en el modal, `$.post` directo a `/guardar_contenido` |
| Campo de contenido | Archivo (`type=file`, máx 1MB) | URL (`type=url`) — acepta `.mp4` directo o link de YouTube |
| Campos extra en crear/editar | — | `imagen_respaldo` (select) e `imagen_respaldo`/`verticalizar` en editar |
| Endpoint crear | vía iframe + submit oculto | `POST /guardar_contenido` directo |
| Endpoint editar | `POST /editar_contenido` | igual, `POST /editar_contenido` |
| Endpoint activar/desactivar | `GET /cambiar_estado_contenido` | igual |
| Endpoint eliminar | `GET /eliminar_elemento` + `validarContenidos` | igual |

## Flujo: Crear (Agregar video)

Modal `#agregarvideo`, SIN iframe. Campos:

| Campo | id | Notas |
|---|---|---|
| Nombre vídeo | `nombre_video` | requerido |
| Descripción vídeo | `descripcion_video` | opcional |
| URL vídeo | `url_video` (`type=url`) | requerido. Formatos aceptados: video directo (`http://.../mov_bbb.mp4`) o YouTube (`https://www.youtube.com/watch?v=...`) |
| Imágen de respaldo | `imagen_respaldo` (select) | **referencia cruzada al submódulo Imágenes** — lista las imágenes ya subidas ahí, para mostrarlas si el video no carga. Confirma que Imágenes y Videos comparten el mismo banco de contenido de fondo. |
| ¿Verticalizar video? | `verticalizar_nuevo` (select Sí/No) | pensado para video vertical en celulares |

Guardar (`#guardar`) valida en cliente (nombre no vacío + sin caracteres especiales, url no vacía) y hace `POST /guardar_contenido` con `tipo_contenido:'video'` y `datos` como array JSON posicional `[nombre, descripcion, url, imagen_respaldo, verticalizar]`. Sin trampa de iframe — mucho más simple que Imágenes.

## Flujo: Editar

Modal `#editarvideo`. Campos: `nuevo_nombre`, `nueva_descripcion`, `nueva_url`, `nueva_imagen_respaldo` (select), `verticalizar` (select). A diferencia de Imágenes (que solo editaba 3 campos), aquí los 5 campos del alta son editables.

Guardar (`#guardaredicion`) → `POST /editar_contenido`, `datos` = `[nombre, descripcion, url, imagen_respaldo, verticalizar]`.

## Flujo: Activar/Desactivar, Eliminar, Vista previa, Asignar

**Idénticos a Imágenes**, mismo HTML (`switch-input` con el mismo `<span>` decorativo que intercepta clics), mismas funciones JS (`bloquear`, `eliminar` con `validarContenidos`, `asignar`). Reutilizo directamente las mismas soluciones ya validadas:
- Toggle: disparar `change` por JS + `expect_response` en vez de clickear el switch.
- Eliminar: esperar visibilidad del popup + pausa antes de "Aceptar" + `expect_response`.

**Particularidad de "Vista previa" en Videos**: si la URL contiene `youtube`, muestra un `<iframe>` embebido de YouTube; si no, un `<video>` HTML5 con el `src` directo. No aplica a nuestro MVP (no estamos automatizando vista previa todavía).

## Hallazgo de timing (crear/editar)

`wait_for_load_state("networkidle")` solo, después de clickear "Guardar", **no alcanza** — el `location.reload()` corre dentro del callback de éxito del `$.post`, y hay una ventana donde la búsqueda posterior corre antes de que ese reload haya efectivamente recargado la tabla con el nuevo registro (falló 2/2 veces en la suite real, aunque un script manual sin grabación de video ni viewport grande sí pasaba — la sobrecarga de grabar video parece alcanzar para exponer la carrera). Se resolvió envolviendo el click en `page.expect_response("**/guardar_contenido**")` (y lo mismo para editar, con `**/editar_contenido**`) para esperar la respuesta real del servidor antes de seguir. **Recomendado aplicar el mismo patrón a cualquier "Crear"/"Editar" de los próximos submódulos**, incluso si en Imágenes no hizo falta (ahí el mecanismo de guardado es distinto, vía iframe).

## Pendiente / a confirmar
- No se automatizó el caso "editar imagen_respaldo/verticalizar" en detalle (se cubre igual que nombre/descripcion/url, mismo mecanismo de fill/select).
- Mismo alcance que Imágenes: por ahora solo "eliminar caso libre" (sin dependencias asignadas).
