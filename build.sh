#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting build process..."

# --- Install Python Dependencies ---
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# --- Database Migration/Initialization (Optional but recommended) ---
echo "Running database migrations..."
python -c "
from app import app, db
with app.app_context():
    try:
        from flask_migrate import upgrade
        upgrade()
        print('Database upgraded successfully.')
    except Exception as e:
        print(f'Error during database upgrade: {e}')
        # Depending on your setup, you might want to raise the exception
        # raise
"

echo "Build process completed successfully."

# --- Important ---
# Do NOT start the application in build.sh.
# build.sh is for BUILDING, not RUNNING.
# Render will run the start command separately after the build.
