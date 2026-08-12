#!/usr/bin/env bash
set -e

source venv/bin/activate

uvicorn server.main:app --reload --port 8000
