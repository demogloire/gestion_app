from flask import Blueprint

stock = Blueprint('stock', __name__, url_prefix='/stock')
# never forget 
from . import routes