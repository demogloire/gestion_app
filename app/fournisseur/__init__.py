from flask import Blueprint

fournisseur = Blueprint('fournisseur','__name__',url_prefix='/fournisseur')

from . import routes