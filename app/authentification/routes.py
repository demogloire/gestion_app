from flask import render_template, flash, url_for, redirect, request
from .. import db, bcrypt
from ..models import Boutique, User 
from app.authentification.forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from . import bp


@bp.route('/register', methods=('GET', 'POST'))
def register():
   return render_template('authentification/register.html')

@bp.route('/', methods=('GET', 'POST'))
@bp.route('/login', methods=('GET', 'POST'))
def login():
   #Verification de l'authentification de l'utilisateur
   if current_user.is_authenticated:
      return redirect(url_for('main.index'))

   form=LoginForm()
   #Verifiation de la connexion à l'envoie du formulaire
   if form.validate_on_submit():
      user=User.query.filter_by(email=form.email.data).first()
      if user and bcrypt.check_password_hash(user.password, form.password.data):
         login_user(user, remember=form.remember.data)
         next_page= request.args.get('next')
         return redirect(next_page) if next_page else redirect(url_for('main.index'))
      else:
         flash("Mot de passe incorrect",'danger') 

   return render_template('authentification/login.html', form=form)