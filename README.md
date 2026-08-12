# AUTOLOG 2.0 — Automatización de Smartwifi

Este proyecto prueba automáticamente la plataforma administrativa de **Smartwifi**
(donde se crean, editan y administran los portales y su contenido), usando
Playwright. Es un proyecto nuevo e independiente de `qa-auto-portales` — ese
sigue probando los portales cautivos (lo que ve el usuario final al conectarse
al wifi); este prueba el panel de administración.

## Qué está probado hoy

**Módulo Contenido Multimedia**, dos submódulos con su ciclo completo:
- **Imágenes**: crear (con archivo), editar, activar/desactivar, eliminar (imagen libre, sin asignar a ningún portal).
- **Videos**: igual, pero con URL en vez de archivo.

Cada corrida queda validada contra el entorno de QA real (`qa.datawifi.co`), no contra datos simulados.

Rompecabezas e Iframes (los otros submódulos de Contenido Multimedia) todavía no están probados — son el siguiente paso.

## Dos formas de correrlo

### 1. Por terminal
```bash
./run_tests.sh
```
Corre todo, genera un reporte y lo abre solo al terminar. Para correr un submódulo puntual:
```bash
./run_tests.sh tests/test_steps_imagenes.py
```

### 2. Por interfaz web
```bash
./run_server.sh
```
Abrí `http://localhost:8000`: seleccionás módulo(s) desde un desplegable (agrupados igual que en el sidebar de Smartwifi), le das "Ejecutar prueba", ves la salida en vivo, y queda guardado en un historial con link al reporte de cada corrida. Pensada para no depender de la terminal en el día a día. **Todavía no tiene login** — solo para uso local por ahora.

## Si el login deja de funcionar

Si un test se cuelga buscando un botón que nunca aparece, o el reporte muestra un timeout esperando algo del panel: la sesión guardada expiró. Hay que volver a loguearse a mano una vez:
```bash
source venv/bin/activate
python scripts/capture_login_state.py
```
Se abre un navegador — completá usuario, contraseña y el captcha como siempre, y cuando veas el panel de Smartwifi cargado, apretá **Resume** (▶) en la ventanita del Inspector de Playwright que aparece (no "Record", ese es otro botón).

**Ojo**: la sesión **no tiene una duración fija garantizada** — a veces duró varios días, otra vez expiró en apenas ~3 horas. No hay que asumir que "ya la renové hoy, seguro aguanta" — si un test falla raro, lo primero a sospechar es esto.

## Qué te queda como evidencia

En el reporte de cada corrida (`reporte_html/reporte.html` por terminal, o el link "Ver reporte" del historial por la interfaz web) vas a encontrar:
- Si pasó o falló cada prueba, con su Módulo/Submódulo/Función.
- El escenario completo en texto (qué hizo el test, paso a paso).
- Un link **"Ver video"** con la grabación de esa corrida específica.

## Ver el navegador en vivo (para aprender o debuggear)

Por defecto las pruebas corren "invisibles" (más rápido, así se corren en CI/automatizado). Para verlas correr en un navegador real, en cámara lenta:
```bash
HEADLESS=0 SLOWMO_MS=400 ./run_tests.sh tests/test_steps_imagenes.py
```

## Estructura del proyecto (resumen)

- `features/` — qué se prueba, descrito en lenguaje simple (Gherkin).
- `tests/` — la conexión entre esos escenarios y el código real.
- `src/tasks/`, `src/questions/` — las acciones concretas sobre Smartwifi (crear imagen, verificar que está activa, etc.) y las reglas especiales de cada pantalla.
- `server/` — la interfaz web (FastAPI + una página HTML simple, sin frameworks de frontend todavía).
- `docs/mapping/` — notas técnicas de cómo está armada cada pantalla del admin (útil si algo se rompe y hay que investigar por qué).
- `docs/session-checkpoints/` — resúmenes de cada sesión de trabajo, para retomar sin perder contexto.
