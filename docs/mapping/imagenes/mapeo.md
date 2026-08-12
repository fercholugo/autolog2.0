# Mapeo — CREA > Contenido multimedia > Imágenes

URL listado: `https://qa.datawifi.co/easyfi/web/app.php/administrar/imagenes`

## Stack detectado
- Symfony (`app.php` front controller, tokens `_token` tipo CSRF en formularios).
- jQuery + Bootstrap 5 (tema admin "Sneat"), tabla con DataTables (`#tabla_imagenes`).
- Casi todas las acciones son `onclick`/`onchange` inline que llaman funciones JS globales (no son links ni forms normales) y disparan `$.get`/`$.post` a endpoints REST-like, luego `location.reload()`.

## Listado (tabla `#tabla_imagenes`)
Columnas: Nombre | Destino | Activar | Administrar.

- **Activar/Desactivar**: checkbox `#switch<id>` con `onchange="bloquear(<id>)"` → `GET /cambiar_estado_contenido` (`tipo_contenido=imagen`, `id_recurso`, `cambio=activar|desactivar`). Solo muestra un toast, no recarga.
- **Administrar** (menú `⋮` por fila, 4 acciones):
  - **Asignar** → `asignar(id)` → abre modal `#asignarimagen`.
  - **Editar** → `mostrar_editar(id, nombre, descripcion, destino, cpm, cpc, fecha_vigencia, fecha_inicio, impactos)` → abre modal `#editarimagen`.
  - **Vista previa** → `vista_previa(url)` → abre modal `#vista_previa_recurso` con un `<img>`.
  - **Eliminar** → `eliminar(id, nombre)` (ver flujo abajo).

## Flujo: Crear (Agregar imagen)
Botón "+ Agregar imagen" abre modal `#agregarimagen`, cuyo body es un **iframe** (`#fragmento`) apuntando a una página completa aparte: `/subir_imagen`. El formulario real vive ahí dentro, con estos campos (confirmado navegando directo a esa URL):

| Campo | id / name | Notas |
|---|---|---|
| Nombre | `product_nombre` (`product[nombre]`) | requerido |
| Descripción | `product_descripcion` | opcional |
| Destino | `product_destino` (`product[destino]`) | máx 150 caracteres, redirige al usuario si el tipo de redirección del portal es "Experiencia usuario" |
| Adjuntar imagen | `product_ruta` (`product[ruta]`) | `type=file`, máx 1MB |
| tipo | `product_tipo` (oculto) | seteado por JS del modal, no por el usuario |
| submit | `enviarformulario` (oculto, `display:none`) | disparado por JS, no clickeable directamente |
| CSRF | `product__token` | token Symfony, se maneja solo mientras se use el form real |

**Trampa clave**: el botón "Guardar" del modal (`#guardar`, fuera del iframe) no envía nada él mismo — lee `product_nombre`/`product_ruta` **dentro del documento del iframe** (`self.fragmento.document`), fuerza `product_tipo = '1-0'`, y hace click programático en el submit oculto del iframe. Para Playwright esto implica usar `page.frame_locator("#fragmento")` para llenar los campos, y clickear el botón `#guardar` de la página principal (no un submit dentro del iframe) para confirmar.

## Flujo: Editar
Modal `#editarimagen` solo expone en el DOM actual: `nuevo_nombre`, `nueva_descripcion`, `nuevo_destino` (+ `id_imagen_editar` oculto). La función `mostrar_editar` también intenta setear `nuevo_cpm`, `nuevo_cpc`, `nuevo_fecha_vigencia`, `nuevo_fecha_inicio`, `nuevo_impactos` — **campos que no existen en el HTML actual** (probablemente resabio de una versión anterior del formulario; jQuery no falla, simplemente no hace nada). No tomar esos nombres como reales.

Guardar (`#guardaredicion`) valida en cliente (nombre sin caracteres especiales, destino ≤150) y hace `POST /editar_contenido` con `datos` como array JSON posicional `[nombre, descripcion, destino, cpm, cpc, fecha_vigencia, impactos, fecha_inicio]` — el orden del array no coincide con el orden de los campos visibles, ojo si alguna vez hay que armar este payload a mano en vez de por UI.

## Flujo: Asignar a portales
Modal `#asignarimagen`: buscador de portal (`input.completar_portales`), checkbox "Seleccionar todos", y una lista de checkboxes `.asignaciones` (uno por portal, con `data-valor`/`title` = nombre del portal). Guardar (`#guardarasignacion`) arma dos listas (asignados/no asignados) y `POST /asignar_contenido`.

Esto confirma la arquitectura: una imagen se **sube una vez** al banco de contenido y se **asigna** a N portales por separado — no se sube "dentro" del editor de cada portal.

## Flujo: Eliminar
`eliminar(id, nombre)` primero valida (`validarContenidos`) si el recurso está en uso:
- **Si está asignado a algo**: abre modal `#recursos_asignados` con una tabla de qué depende de él — **bloquea el borrado**, no hay opción de forzar.
- **Si no está en uso**: pide confirmación (diálogo tipo SweetAlert) y luego `GET /eliminar_elemento`.

Para automatizar hay que cubrir ambas ramas (imagen libre vs. imagen asignada) como dos escenarios distintos, no uno solo con happy path.

## Hallazgos de automatizacion (confirmados corriendo el flujo real contra QA)

- **Crear exige archivo aunque el HTML no lo marque `required`**: el botón "Guardar" del modal valida en JS que `product_nombre` Y `product_ruta` (el archivo) sean no-vacíos; sin archivo tira "Por favor llene los campos minimos" y no llega a enviar el formulario. Toda automatización de creación necesita adjuntar un archivo.
- **El switch "Activar" no es clickeable de forma confiable**: el `<span class="switch-on">` decorativo se superpone al `<input>` real e intercepta los clics (confirmado: Playwright reporta "intercepts pointer events" con click normal, con `force=True`, y hasta con `.click()` nativo vía `evaluate` — ninguno lo togglea consistentemente). Solución aplicada: disparar directamente el evento `change` sobre el input (`el.checked = valor; el.dispatchEvent(new Event('change'))`), que ejecuta el mismo `onchange="bloquear(...)"` real de la página, y esperar la respuesta HTTP real de `/cambiar_estado_contenido` antes de continuar (no timings arbitrarios).
- **El popup de confirmación de "Eliminar" (SweetAlert2) tiene animación de entrada**: clickear "Aceptar" apenas se detecta visible puede caer durante la transición y no registrarse (el click se pierde silenciosamente, sin error). Se resolvió esperando explícitamente su visibilidad + una pequeña pausa antes del click, y confirmando con `expect_response` que `/eliminar_elemento` efectivamente se disparó. Con ese fix, el ciclo completo (crear → editar → activar/desactivar → eliminar) corrió 2/2 veces limpio de punta a punta contra QA real.

## Pendiente / a confirmar
- Ver si "Videos", "Rompecabezas" e "Iframes" comparten el mismo patrón (modal con iframe a página `/subir_x`, editar con campos limitados, asignar a portales, eliminar con validación de dependencias) o cada uno tiene variaciones.
- Confirmar contigo si conviene automatizar el flujo de "Eliminar con dependencias" (bloqueado) como caso de prueba explícito, ya que es una regla de negocio real, no solo un detalle de UI.
