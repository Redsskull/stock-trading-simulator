#!/bin/bash
pip install -r requirements.txt
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully!')
"
