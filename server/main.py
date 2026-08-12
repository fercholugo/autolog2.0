"""Servidor FastAPI: endpoints REST + WebSocket para AUTOLOG 2.0 Smartwifi."""

import asyncio
import json
import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server import database, runner

BASE_DIR = Path(__file__).parent
PROJECT_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
REPORTE_DIR = PROJECT_DIR / "reporte_html"
EVIDENCIA_DIR = PROJECT_DIR / "evidencia" / "videos"
SUBMODULOS_FILE = BASE_DIR / "submodulos.json"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    yield


REPORTE_DIR.mkdir(parents=True, exist_ok=True)
(PROJECT_DIR / "evidencia").mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AUTOLOG 2.0 SMARTWIFI", lifespan=lifespan)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/reportes", StaticFiles(directory=str(REPORTE_DIR)), name="reportes")
# Los reportes referencian los videos con rutas relativas tipo
# "../../../evidencia/videos/<run_id>/x.webm" (calculadas por conftest.py
# contra el filesystem real) -- al servirse por HTTP esas rutas relativas
# resuelven a "/evidencia/...", asi que esa ruta tiene que existir tambien.
app.mount("/evidencia", StaticFiles(directory=str(PROJECT_DIR / "evidencia")), name="evidencia")


class RunRequest(BaseModel):
    submodulo_ids: list[str] = []


def _cargar_submodulos():
    """Estructura anidada Modulo -> [Submodulos], tal como esta en Smartwifi."""
    with open(SUBMODULOS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _submodulos_planos():
    """Version aplanada, con el nombre del modulo colgado en cada submodulo,
    para poder buscar por id sin importar de que modulo viene."""
    planos = []
    for grupo in _cargar_submodulos():
        for s in grupo["submodulos"]:
            planos.append({**s, "modulo": grupo["modulo"]})
    return planos


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/submodulos")
async def get_submodulos():
    return _cargar_submodulos()


@app.post("/run")
async def run_test(body: RunRequest, background_tasks: BackgroundTasks):
    seleccionados = [s for s in _submodulos_planos() if s["id"] in body.submodulo_ids]
    if not seleccionados:
        raise HTTPException(status_code=400, detail="Modulo(s) no encontrados")

    por_modulo: dict[str, list[str]] = {}
    for s in seleccionados:
        por_modulo.setdefault(s["modulo"], []).append(s["nombre"])
    nombres = "; ".join(f"{modulo}: {', '.join(subs)}" for modulo, subs in por_modulo.items())

    steps_files = [s["steps"] for s in seleccionados]

    run_id = await database.crear_run(nombres)
    background_tasks.add_task(runner.ejecutar_test, run_id, steps_files)
    return {"run_id": run_id, "estado": "running"}


@app.websocket("/live/{run_id}")
async def websocket_live(websocket: WebSocket, run_id: str):
    await websocket.accept()

    for _ in range(50):
        if run_id in runner.output_queues:
            break
        await asyncio.sleep(0.1)

    if run_id not in runner.output_queues:
        await websocket.close()
        return

    for line in runner.output_store.get(run_id, []):
        try:
            await websocket.send_text(line)
        except Exception:
            return

    q = runner.output_queues[run_id]
    while True:
        try:
            line = await asyncio.wait_for(q.get(), timeout=300)
            if line is None:
                break
            await websocket.send_text(line)
        except asyncio.TimeoutError:
            break
        except WebSocketDisconnect:
            return

    try:
        await websocket.close()
    except Exception:
        pass


@app.get("/status/{run_id}")
async def get_status(run_id: str):
    run = await database.obtener_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run no encontrado")
    return run


@app.get("/history")
async def get_history():
    return await database.listar_runs()


@app.delete("/history/{run_id}")
async def delete_history(run_id: str):
    run = await database.obtener_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run no encontrado")
    await database.eliminar_run(run_id)
    shutil.rmtree(REPORTE_DIR / "runs" / run_id, ignore_errors=True)
    shutil.rmtree(EVIDENCIA_DIR / run_id, ignore_errors=True)
    return {"ok": True}
