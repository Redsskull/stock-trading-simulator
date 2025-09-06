#!/bin/bash
set -e

# Run migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Start the app with gunicorn
gunicorn app:app
