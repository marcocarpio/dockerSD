from flask import Flask
from flask_cors import CORS
from app.extensions import db
from app.api.routes.auth import auth_bp

def create_app(script_info=None):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object('app.config.Config')
    db.init_app(app)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.api.blueprints.foo import foo_blueprint
    app.register_blueprint(foo_blueprint)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
