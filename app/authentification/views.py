from flask import render_template
from . import bp

@bp.route('/register', methods=('GET', 'POST'))
def register():
   return render_template('authentification/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
   return render_template('authentification/login.html')