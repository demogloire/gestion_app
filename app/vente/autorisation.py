import os
import secrets
from flask import render_template, flash, url_for, redirect, request, session
from flask_login import login_user, current_user, login_required
from PIL import Image
from .. import create_app
from .. import db, vente
from functools import wraps

from ..models import Produit, Facture, Client, Typeclient 


config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)


#Autorisation des vendeur
def autorisation_vendeur(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role =='Vendeur':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))       
    return wrap