"""Historial de ejecuciones en SQLite (misma idea que qa-auto-portales)."""

import aiosqlite
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "reporte_html" / "autolog_history.db"
COLOMBIA_TZ = timezone(timedelta(hours=-5))


async def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id            TEXT PRIMARY KEY,
                fecha         TEXT NOT NULL,
                modulos_nombre TEXT NOT NULL,
                estado        TEXT NOT NULL DEFAULT 'running',
                ruta_reporte  TEXT,
                duracion_seg  REAL,
                log           TEXT
            )
        """)
        await db.commit()


async def crear_run(modulos_nombre: str) -> str:
    run_id = str(uuid.uuid4())[:8]
    fecha = datetime.now(COLOMBIA_TZ).strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO runs (id, fecha, modulos_nombre, estado) VALUES (?, ?, ?, 'running')",
            (run_id, fecha, modulos_nombre),
        )
        await db.commit()
    return run_id


async def actualizar_run(run_id: str, estado: str, ruta_reporte: str | None, duracion_seg: float, log: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE runs SET estado=?, ruta_reporte=?, duracion_seg=?, log=? WHERE id=?",
            (estado, ruta_reporte, duracion_seg, log, run_id),
        )
        await db.commit()


async def listar_runs(limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, fecha, modulos_nombre, estado, ruta_reporte, duracion_seg "
            "FROM runs ORDER BY fecha DESC LIMIT ?",
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def obtener_run(run_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM runs WHERE id=?", (run_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def eliminar_run(run_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM runs WHERE id=?", (run_id,))
        await db.commit()
