from flask import Blueprint

vente = Blueprint('vente', __name__, url_prefix='/vente')
# never forget 
from . import routes