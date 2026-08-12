# Notas generales (aplican a todo el sitio, no a un submódulo puntual)

## El sitio puede arrancar en inglés (Weglot)

Smartwifi usa un widget de traducción automática (Weglot, visto en el dropdown de idioma del navbar: `data-idioma="wg-es"`, `wg-en"`, etc.). Sin indicarle explícitamente el idioma a Playwright, una sesión nueva puede arrancar en **inglés** — mismo layout, mismos ids/selectores por `id`, pero **el texto visible cambia** ("Agregar video" → "Add video", "Imágenes" → "Images", etc.). Como casi todos nuestros selectores usan `get_by_role(..., name="texto en español")`, esto rompe todo lo que dependa de texto visible, con un error de timeout que parece (pero no es) sesión expirada.

**Síntoma**: `Timeout 30000ms exceeded... waiting for get_by_role("button", name="Agregar X")`, pero la navegación llegó bien a la pantalla correcta (no redirigió a `/login`). Para diferenciarlo de una sesión expirada de verdad: mirar el título de la página o el idioma del menú lateral en el screenshot/HTML volcado — si dice "Welcome" en vez de "Bienvenido", es esto, no la sesión.

**Fix aplicado**: `locale="es-ES"` al crear el `BrowserContext`, tanto en `src/abilities/browse_the_web.py` (todas las corridas) como en `scripts/capture_login_state.py` (la captura manual de sesión). Confirmado que resuelve el problema de forma consistente.

**Por qué importa para submódulos futuros**: cualquier Task/Question nueva que use `get_by_role(..., name="...")` con texto en español depende de esto. Si en algún momento se ve un fallo similar (timeout esperando un botón que "debería estar"), revisar primero si el locale se está aplicando (por ejemplo, si se arma un `BrowserContext` a mano en un script nuevo sin pasar por `BrowseTheWeb.using_saved_session`).
