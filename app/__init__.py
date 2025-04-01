import os
from flask import Flask
from flask_login import LoginManager
from config import ProductionConfig, DevelopmentConfig


# Create login_manager as a global variable
login_manager = LoginManager()

def create_app(prod_config=True):
    # Create Flask app instance
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    if prod_config:
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize database
    from . import db

    # Register database callbacks
    app.teardown_appcontext(db.close_db)

    # Register CLI commands - moved here
    from app.migrations.migration_cli import migrations_cli
    app.cli.add_command(migrations_cli)

    # Initialize database tables
    with app.app_context():
        db.init_db()

    # Register blueprints
    from app.routes.auth_routes import bp as auth_bp
    from app.routes.article_routes import bp as article_bp
    from app.routes.сomment_routes import bp as comment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(article_bp)
    app.register_blueprint(comment_bp)

    # Регистрируем блюпринты
    from webhook_handler import webhook
    app.register_blueprint(webhook)

    return app