from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Categorie, Produit, Depot
from app.boutique.autorisation import autorisation_gerant
from app.depot.forms import DepotForm, DepotEditForm

from flask_login import login_user, current_user, logout_user, login_required

from . import depot

@depot.route('/ajouter_depot', methods=['GET','POST'])
@login_required
@autorisation_gerant
def ajouterdepot():
    #Les dépots
    title="Ajouter un dépôt"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=DepotForm()

    if form.validate_on_submit():
        depot=Depot(nom_depot=form.nom_depot.data.capitalize())
        db.session.add(depot)
        db.session.commit()
        flash('Vous avez ajouté ({}) comme dépôt'.format(form.nom_depot.data.capitalize()),'success')
        return redirect(url_for('depot.index'))

    return render_template('depot/ajouterc.html', title=title, form=form)



@depot.route('/')
@login_required
@autorisation_gerant
def index():

    title="Liste | dépôt"
    #Requete de listage des dépôts
    list_depot=Depot.query.all()

    return render_template('depot/index.html', title=title, listes=list_depot)


@depot.route('/<int:dep_id>/depot', methods=['GET','POST'])
@login_required
def editer_depot(dep_id):

    # #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))
        
    #formulaire
    form=DepotEditForm()
    #Verification de l'existence de dépôt
    dep_edit=Depot.query.filter_by(id=dep_id).first_or_404()
    #Titre de la catégorie
    title=" {} | Modification "+dep_edit.nom_depot

    #Validation d'enregistrement
    if form.validate_on_submit():
        dep_edit.nom_depot=form.nom_depot.data.capitalize()
        db.session.commit()
        flash("Modification avec succès",'success')
        return redirect(url_for('depot.index'))
    elif request.method =='GET':
        form.nom_depot.data=dep_edit.nom_depot

    return render_template('depot/depotedit.html', title=title, form=form)

