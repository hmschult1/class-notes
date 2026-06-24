"""Application factory and extension initialization.

This module uses the Flask application factory pattern. It initializes
extensions (SQLAlchemy, Flask-Migrate, CSRF protection) without creating
an application instance at import time so the app can be configured for
different environments during testing or deployment.

Only the alumni update form blueprint (`form_bp`) is registered here;
authentication and dashboard blueprints were intentionally removed to
keep this project focused on the alumni update workflow.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    # Create the Flask app instance
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # --- Register Blueprints ---
    from app.routes import form_bp
    app.register_blueprint(form_bp)
    
    # --- debugging 404s ---
    # with app.app_context():
        # print(app.url_map)

    return app