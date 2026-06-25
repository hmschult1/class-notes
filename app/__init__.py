"""Application factory and extension initialization."""

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(override=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from config import Config

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import models so Flask-Migrate can discover them
    from app import models

    # Register blueprints
    from app.routes import form_bp
    app.register_blueprint(form_bp)

    return app