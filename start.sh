#!/bin/bash
set -e

# Run migrations
flask db upgrade

# Start the app with gunicorn
gunicorn app:app
