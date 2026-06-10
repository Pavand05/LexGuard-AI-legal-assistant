"""
Shared Flask extension instances.
Importing from here avoids circular imports between app.py, models.py, auth.py.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

db  = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
