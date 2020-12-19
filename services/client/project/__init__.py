import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# import sys
# print(app.config, file=sys.stderr)

def create_app(script_info=None):
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # zou normaal uit app_settings moeten komen, ma werkte niet direct
    app.config['SECRET_KEY'] = "top_secretahgdhjvdjksdfkjfdsjdsajkfkjasdjfjksdakjfasdjkfjksadjkfkjasdfjkasdkjf"

    # set up extensions
    db.init_app(app)

    # register blueprints
    # from project.api.clubs import clubs_blueprint
    # app.register_blueprint(clubs_blueprint)


    from project.api.divisions import divisions_blueprint
    app.register_blueprint(divisions_blueprint)

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
