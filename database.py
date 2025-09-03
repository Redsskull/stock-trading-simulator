# I couldn't find a way to avoid circular imports while learning sqlalchemy without a third FileExistsError
from flask_sqlalchemy import SQLAlchemy

# Create the database instance
db = SQLAlchemy()
