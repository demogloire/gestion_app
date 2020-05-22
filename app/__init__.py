import os
from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import flask_sijax
#Importation des configuration de l'application sur le developpement de l'application
from config import app_config



db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


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
    bcrypt.init_app(app)
    login_manager.init_app(app)
    #wtf_tinymce.init_app(app)
    

    login_manager.login_message = "Veuillez vous connecté"
    login_manager.login_view = "auth.login"
    login_manager.login_message_category ='danger'
    #SimpleMDE(app)

    # enregistrement des blueprint
    from . import authentification
    app.register_blueprint(authentification.bp)

    #Catégorie des produits
    from .categorie import categorie as categorie_blueprint
    app.register_blueprint(categorie_blueprint)

    #Produit 
    from .produit import produit as produit_blueprint
    app.register_blueprint(produit_blueprint)

    #Fournisseur
    from .fournisseur import fournisseur as fournisseur_blueprint
    app.register_blueprint(fournisseur_blueprint)

    #Depot
    from .depot import depot as depot_blueprint
    app.register_blueprint(depot_blueprint)

    #boutique
    from .boutique import boutique as boutique_blueprint
    app.register_blueprint(boutique_blueprint)

    #Utilisateur
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    #Dashboard
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #Stock
    from .stock import stock as stock_blueprint
    app.register_blueprint(stock_blueprint)

    #Vente
    from .vente import vente as vente_blueprint
    app.register_blueprint(vente_blueprint)

    #Depense
    from .depense import depense as depense_blueprint
    app.register_blueprint(depense_blueprint)

    #Client
    from .client import client as client_blueprint
    app.register_blueprint(client_blueprint)

    #comptes
    from .comptes import comptes as comptes_blueprint
    app.register_blueprint(comptes_blueprint)

    #comptes
    from .inventaire import inventaire as inventaire_blueprint
    app.register_blueprint(inventaire_blueprint)
    




    return app

from . import models