from flask import Blueprint

categorie = Blueprint('categorie','__name__',url_prefix='/categorie')

from . import routes