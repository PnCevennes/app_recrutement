'''
Démarrage de l'application
'''
import os

import flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail


db = SQLAlchemy()
mail = Mail()
cors = CORS()

app_globals = {}

def get_app():
    if app_globals.get('app', False):
        return app_globals['app']
    app = flask.Flask(__name__)
    app.config.from_pyfile('./config.py')
    db.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    app_globals['app'] = app


    # Import des modules coeur
    from core.utils import registered_modules
    from core import routes
    app.register_blueprint(routes.main)

    # Import des modules applicatifs
    import modules

    for prefix, blueprint in registered_modules.items():
        app.register_blueprint(blueprint, url_prefix=prefix)

    return app



if __name__ == '__main__':
    app = get_app()
    from flask_script import Manager
    Manager(app).run()
