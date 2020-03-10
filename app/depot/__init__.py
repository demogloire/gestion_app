from flask import Blueprint

depot = Blueprint('depot','__name__',url_prefix='/depot')

from . import routes