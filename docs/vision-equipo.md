# Visión del equipo vs. estado real del proyecto

_Última actualización: 2026-08-12, a partir de un acta/diagrama compartido por el equipo de Fernando._

Este documento existe para que, al retomar el proyecto en otra máquina (o después de un tiempo sin tocarlo), quede claro **hacia dónde apunta el equipo** y **qué tan lejos o cerca está el código de hoy** de esa visión. No es una lista de tareas — es contexto para tomar decisiones de diseño sin tener que releer el acta original.

## Lo que pidió el equipo

Prioridad #1 declarada explícitamente: **"Automatizar flujos"**.

El flujo completo que describieron:

1. **Login** (en la interfaz): usuario/contraseña, más un selector de **"Plataforma a testear"** y **"Lista de ambientes"** — ambos alimentados desde una base de datos. Esto implica que, a futuro, el proyecto no sería solo "Smartwifi en QA" sino potencialmente **varias plataformas y varios ambientes** (QA, staging, prod, lo que sea).
2. **Elegir alcance**: "probar módulo específico" o "testeo completo" — también desde una tabla `modulos` en base de datos.
3. **Los flujos son de primera clase, independientes entre sí**: para cada módulo, **crear, editar, eliminar y asignación** son 4 flujos separados, cada uno con su propio archivo `.feature`/`.test` y su propia fila de resultado (estado ok/error + evidencia en video) — no un solo escenario que hace las 4 cosas seguidas.
4. Todo esto modelado con tablas de base de datos (plataformas, ambientes, módulos, flujos), no con archivos de configuración sueltos.

## Dónde está el proyecto hoy, comparado con eso

| Punto de la visión | Estado |
|---|---|
| Automatizar flujos | ✅ Hecho para Imágenes y Videos (crear/editar/activar-desactivar/eliminar, de punta a punta contra QA real) |
| Elegir módulo específico o testeo completo | ✅ Cubierto — selector con checkboxes + "Seleccionar todos" en la interfaz web, aunque la lista sale de un JSON (`server/submodulos.json`), no de una base de datos |
| Login en la interfaz | ❌ No existe. Hoy la autenticación contra Smartwifi se resuelve aparte, a mano, una vez (`scripts/capture_login_state.py`) — la interfaz web (`server/`) no le pide credenciales a quien la usa |
| Selector de Plataforma / Ambiente | ❌ No existe. Todo está fijo a Smartwifi + QA (`src/utils/config.py`) |
| Flujos independientes (crear/editar/eliminar/asignar por separado, cada uno con su propio estado y evidencia) | ❌ Diferente. Hoy cada submódulo es **un solo escenario** de "ciclo completo" (`tests/test_steps_imagenes.py`, `tests/test_steps_videos.py`) que hace crear→editar→activar/desactivar→eliminar en una sola corrida. No se puede re-correr "solo eliminación", por ejemplo |
| Flujo de **asignación** (asignar contenido a un portal) | ❌ Explícitamente fuera de alcance por ahora (decisión tomada: "por ahora solo el caso libre" al hablar del borrado). El equipo lo trata como flujo de primera clase, al mismo nivel que crear/editar/eliminar |
| Base de datos para plataformas/ambientes/módulos/flujos | ❌ Hoy es un archivo JSON simple. Funciona bien mientras sea solo Smartwifi con pocos módulos; si crece a varias plataformas, una base de datos real escala mejor |

## Por qué existe esta diferencia (no es un error, es una decisión consciente)

El equipo ya sabía y estuvo de acuerdo en que Fernando iba a enfocarse primero 100% en `qa-auto-portales`, y que este proyecto (`autolog_2_0`) arrancó como algo exploratorio/de aprendizaje en paralelo. Se decidió deliberadamente **empezar simple** (un solo producto, un solo ambiente, sin login, JSON en vez de base de datos) para poder avanzar rápido y aprender Playwright sin la complejidad de un sistema multi-plataforma desde el día uno.

## Cómo usar este documento

Antes de diseñar la próxima pieza grande (login de la interfaz, un nuevo submódulo, la estructura de flujos, etc.), releer esta tabla. Si el equipo ya necesita multi-plataforma o flujos independientes en el corto plazo, conviene decidirlo **antes** de seguir agregando código sobre la estructura simple actual (cambiar la arquitectura después de tener 5-6 submódulos ya escritos sale más caro que decidirlo ahora).
