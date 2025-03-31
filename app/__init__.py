import os
from flask import Flask
from flask_login import LoginManager

# Create login_manager as a global variable
login_manager = LoginManager()

def create_app(test_config=None):
    # Create Flask app instance
    app = Flask(__name__, instance_relative_config=True)

    # проверяем, что директория instance существует
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'blog.db'),
    )

    if test_config is None:
        # Load config.py if not testing
        app.config.from_object('config.DevelopmentConfig')
    else:
        # Load test config if passed in
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize login manager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Initialize database
    from . import db

    # Register database callbacks
    app.teardown_appcontext(db.close_db)

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

    return app