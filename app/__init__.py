from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect

# Initialize extensions (no app yet — factory pattern)
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

# Flask-Login config
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    # Create the Flask app instance
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # --- Register the user loader here ---
    from app.auth_models import User

    @login_manager.user_loader
    def load_user(user_id):
        """Given a user_id, return the corresponding User object."""
        return User.query.get(int(user_id))

    # --- Register Blueprints ---
    from app.routes import auth_bp, dashboard_bp, form_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(form_bp)
    
    # --- debugging 404s ---
    # with app.app_context():
        # print(app.url_map)

    return app