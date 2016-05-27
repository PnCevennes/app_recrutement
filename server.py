#coding: utf8

'''
Démarrage de l'application
'''


import flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_app():
    app = flask.Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    import routes
    app.register_blueprint(routes.main)

    from modules.thesaurus import routes as routes_th
    app.register_blueprint(routes_th.routes, url_prefix='/thesaurus')

    from modules.agents import routes as  routes_ag
    app.register_blueprint(routes_ag.routes, url_prefix='/agents')

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
