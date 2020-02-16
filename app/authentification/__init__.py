from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix='/auth')
# never forget 
from . import views