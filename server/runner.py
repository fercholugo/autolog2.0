"""Ejecuta los tests de pytest como subprocess y transmite el output en tiempo real.

A diferencia de qa-auto-portales, ac  no hace falta un subprocess por
modulo: un solo pytest corriendo varios archivos de test ya genera un
unico reporte self-contained con una fila (y su propio video) por modulo,
gracias a como esta armado tests/conftest.py.
"""

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

PROJECT_DIR = Path(__file__).parent.parent

# Almacen en memoria por run_id: lineas capturadas y cola para streaming
output_store: Dict[str, List[str]] = {}
output_queues: Dict[str, asyncio.Queue] = {}


async def ejecutar_test(run_id: str, steps_files: list[str]):
    """Lanza pytest en background, captura stdout linea a linea,
    actualiza SQLite al terminar y senala fin del stream."""
    from server import database

    output_store[run_id] = []
    output_queues[run_id] = asyncio.Queue()

    async def _emit(line: str):
        output_store[run_id].append(line)
        await output_queues[run_id].put(line)
        print(line, end="", flush=True)

    report_dir = PROJECT_DIR / "reporte_html" / "runs" / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "reporte.html"

    inicio = time.time()
    estado = "error"
    ruta_relativa = None

    cmd = [
        sys.executable, "-m", "pytest",
        *steps_files, "-v", "-s",
        f"--html={report_path}",
        "--self-contained-html",
    ]
    env = {
        **os.environ,
        "HEADLESS": "1",
        "VIDEO": "1",
        "VIDEO_DIR": f"evidencia/videos/{run_id}",
    }

    await _emit(f"[Runner] Modulos: {', '.join(steps_files)}\n")
    await _emit(f"[Runner] Comando: {' '.join(cmd[2:])}\n\n")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
            cwd=str(PROJECT_DIR),
        )
        async for raw in proc.stdout:
            await _emit(raw.decode("utf-8", errors="replace"))
        await proc.wait()
        estado = "done" if proc.returncode == 0 else "error"

        if report_path.exists():
            ruta_relativa = f"runs/{run_id}/reporte.html"

    except Exception as e:
        await _emit(f"[Error critico] {e}\n")

    duracion = round(time.time() - inicio, 1)
    await _emit(f"\n[Runner] Finalizado - Estado: {estado.upper()} ({duracion}s)\n")
    if ruta_relativa:
        await _emit(f"[Runner] Reporte disponible: /reportes/{ruta_relativa}\n")

    log_completo = "".join(output_store[run_id])
    await database.actualizar_run(run_id, estado, ruta_relativa, duracion, log_completo)

    # Senal de fin de stream para el WebSocket
    await output_queues[run_id].put(None)
