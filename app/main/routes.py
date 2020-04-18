from flask import render_template, flash, url_for, redirect, request, session
from .. import db
from flask_login import login_user, current_user, logout_user, login_required

from . import main



@main.route('/')
@login_required
def index():
    title="Dashboard"
    option_encours="das"

    return render_template('main/index.html', title=title,option_encours=option_encours)

