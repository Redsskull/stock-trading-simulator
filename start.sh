#!/bin/bash
# Source the virtual environment first
source /opt/render/project/src/.venv/bin/activate

# Run database migrations
echo "Running database migrations..."
python -c "from app import app; from flask_migrate import upgrade; with app.app_context(): upgrade()"
echo "Database migrations completed successfully"

# Start the application
exec python -m gunicorn -b :$PORT app:app
