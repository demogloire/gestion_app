from flask import Blueprint

depense = Blueprint('depense','__name__',url_prefix='/depense')

from . import routes