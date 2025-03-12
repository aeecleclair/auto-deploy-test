#!/usr/bin/env bash
set -e

echo "Running migrations..."
# We set an environment variable to tell workers to avoid initializing the database
# as we want to do it only once before workers are created by Unicorn
export HYPERION_INIT_DB="False"
# python3 init.py

echo "Starting FastAPI server..."
exec fastapi run app/entrypoints/fastapi_app.py --workers ${NB_WORKERS:-1}
