from flask import Flask
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect

# Initialize extensions (no app yet — factory pattern)
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