import os
from pathlib import Path
from flask import Flask, render_template
from config import config
from app.extensions import db, login_manager, csrf


def create_app(config_name: str = None) -> Flask:
    """
    Application factory for Fake Job and Internship Detection System.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app_config = config.get(config_name, config['default'])
    app.config.from_object(app_config)

    # Ensure instance directory exists for SQLite
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.main import main_bp
    from app.auth.routes import auth_bp
    from app.analysis import analysis_bp
    from app.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(admin_bp)

    # Register error handlers
    register_error_handlers(app)

    # Global template context processor
    @app.context_processor
    def inject_global_template_vars():
        from datetime import datetime
        return {
            'current_year': datetime.now().year,
            'app_name': 'Fake Job & Internship Detection System',
            'app_version': '1.0.0'
        }

    # Automatically create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app


def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

