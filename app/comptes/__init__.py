from flask import Blueprint

comptes = Blueprint('compte','__name__',url_prefix='/compte')

from . import routes