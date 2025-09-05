#!/bin/bash
export PATH="/usr/bin:$PATH"

# Exit on error
set -e

# Run database migrations
echo "Running database migrations..."
python3 -c "from app import app, db; from flask_migrate import upgrade; app.app_context().push(); upgrade()"

echo "Database migrations completed successfully"

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:${PORT:-10000} app:app
