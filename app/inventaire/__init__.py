from flask import Blueprint

inventaire = Blueprint('inventaire','__name__',url_prefix='/inventaire')

from . import routes