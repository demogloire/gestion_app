from flask import render_template, flash, url_for, redirect, request
from .. import db
from flask_login import login_user, current_user, logout_user, login_required

from . import main



@main.route('/')
@login_required
def index():
    title="Dashboard"
    return render_template('main/index.html', title=title)

