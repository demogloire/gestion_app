from flask import Blueprint

boutique = Blueprint('boutique','__name__',url_prefix='/boutique')

from . import routes