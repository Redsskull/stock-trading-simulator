#!/bin/bash
set -e

echo "Running database migrations..."
python3 -c "from app import app; from flask_migrate import upgrade; with app.app_context(): upgrade()"

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:${PORT:-10000} app:app
