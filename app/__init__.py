import os
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_sijax
from flask_login import LoginManager

from config import app_config

db = SQLAlchemy()
login_manager= LoginManager()


path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

def create_app(config_name):
    # Les configuration de l'application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    
    #Sijax initialisation
    app.config['SIJAX_STATIC_PATH'] = path
    app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
    flask_sijax.Sijax(app)

    # enregistrement des extension 
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    # enregistrement des blueprint
    from . import authentification
    app.register_blueprint(authentification.bp)

    #Catégorie des produits
    from .categorie import categorie as categorie_blueprint
    app.register_blueprint(categorie_blueprint)



    return app

from . import models