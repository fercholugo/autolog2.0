import os

import pytest
from playwright.sync_api import sync_playwright

from src.abilities.browse_the_web import BrowseTheWeb
from src.actors.actor import Actor

# HEADLESS=0 para ver el navegador; SLOWMO_MS para pausar N ms entre cada
# accion de Playwright y poder seguir el flujo a simple vista.
# VIDEO=0 para desactivar la grabacion (esta prendida por defecto).
HEADLESS = os.environ.get("HEADLESS", "1") != "0"
SLOWMO_MS = int(os.environ.get("SLOWMO_MS", "0"))
# VIDEO_DIR permite aislar los videos de una corrida puntual (la interfaz
# web la usa para poner cada corrida en su propia carpeta y poder borrarla
# entera despues); por CLI casi nunca hace falta tocarla.
VIDEO_DIR = os.environ.get("VIDEO_DIR", "evidencia/videos") if os.environ.get("VIDEO", "1") != "0" else None


@pytest.fixture
def actor(request):
    with sync_playwright() as playwright:
        browse_the_web = BrowseTheWeb.using_saved_session(
            playwright, headless=HEADLESS, slow_mo=SLOWMO_MS, video_dir=VIDEO_DIR
        )
        admin = Actor("Administrador").can(browse_the_web)
        if browse_the_web.page.video is not None:
            # La ruta es determinística desde que se crea la page (Playwright
            # la asigna de antemano); hay que setearla ANTES del yield para
            # que ya este disponible cuando corre el hook de la fase "call".
            # El archivo en si recien queda completo al cerrar el browser.
            request.node.video_path = browse_the_web.page.video.path()
        yield admin
        browse_the_web.quit()


# --- Hooks de pytest-bdd: imprimen cada paso Given/When/Then en consola a
# medida que se ejecuta, sin tener que agregar un print() en cada step. ---


def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    print(f"\n  {step.keyword.upper():6} {step.name}")


def pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception):
    print(f"  -> FALLO: {exception}")


def _parse_tags(tags):
    """Convierte tags tipo 'modulo:Contenido-Multimedia' en {'modulo': 'Contenido Multimedia'}."""
    resultado = {}
    for tag in tags:
        if ":" in tag:
            clave, valor = tag.split(":", 1)
            resultado[clave] = valor.replace("-", " ")
    return resultado


def pytest_bdd_before_scenario(request, feature, scenario):
    # Guarda en el item info legible (Modulo/Submodulo/Funcion, sacada de
    # tags @modulo:x @submodulo:y @funcion:z) y el texto Gherkin completo,
    # para que los hooks de pytest-html los usen mas abajo.
    info = _parse_tags(feature.tags)
    info.update(_parse_tags(scenario.tags))
    request.node.qa_label = (
        f"<b>Modulo:</b> {info.get('modulo', '-')}<br>"
        f"<b>Submodulo:</b> {info.get('submodulo', '-')}<br>"
        f"<b>Funcion:</b> {info.get('funcion', scenario.name)}"
    )

    pasos = "\n".join(f"    {step.keyword} {step.name}" for step in scenario.steps)
    request.node.qa_gherkin = f"Feature: {feature.name}\n\n  Scenario: {scenario.name}\n{pasos}"


# --- Reporte HTML (pytest-html): titulo, columna "Test" legible, Gherkin en
# el area de logs (en vez de "No log output captured."), y link al video. ---

try:
    from pytest_html import extras as html_extras
except ImportError:
    html_extras = None


def pytest_html_report_title(report):
    report.title = "AUTOLOG 2.0 SMARTWIFI"


def pytest_html_results_summary(prefix, summary, postfix, session):
    # Oculta la seccion "Environment": no aporta nada en este reporte.
    postfix.append("<style>#environment, #environment-header { display: none !important; }</style>")


def pytest_html_results_table_row(report, cells):
    if getattr(report, "qa_label", None):
        cells[1] = f'<td class="col-testId">{report.qa_label}</td>'


def pytest_html_results_table_html(report, data):
    if getattr(report, "qa_gherkin", None):
        data[:] = [f"<pre>{report.qa_gherkin}</pre>"]


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    report.qa_label = getattr(item, "qa_label", None)
    report.qa_gherkin = getattr(item, "qa_gherkin", None)

    video_path = getattr(item, "video_path", None)
    if not video_path or not os.path.exists(video_path):
        return

    html_path = getattr(item.config.option, "htmlpath", None) or "reporte_html/reporte.html"
    rel_path = os.path.relpath(video_path, start=os.path.dirname(html_path))
    report.extras = getattr(report, "extras", [])
    if html_extras:
        report.extras.append(html_extras.url(rel_path, "Ver video"))
    else:
        report.extras.append(f'<a href="{rel_path}" target="_blank">Ver video</a>')
