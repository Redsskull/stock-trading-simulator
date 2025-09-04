#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "
from app import app, db
with app.app_context():
    from flask_migrate import upgrade
    upgrade()
    print('Database tables created successfully!')
"
