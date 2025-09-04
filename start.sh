#!/bin/bash
# Run database migrations (this happens at runtime when DATABASE_URL is available)
python -c "from app import app; from flask_migrate import upgrade; with app.app_context(): upgrade()"
echo "Database migrations completed successfully"

# Start the application
exec python -m gunicorn -b :$PORT app:app
