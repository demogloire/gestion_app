from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Boutique 
from app.boutique.forms import BoutiqueForm, BoutiqueEditerForm
from app.boutique.autorisation  import autorisation_gerant
from flask_login import login_user, current_user, logout_user, login_required

from . import boutique

@boutique.route('/ajouter_boutique', methods=['GET','POST'])
@login_required
@autorisation_gerant
def ajouterboutique():
    #Boutique 
    title="Ajouter une boutique"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=BoutiqueForm()

    if form.validate_on_submit():
        ajout_boutique=Boutique(nom_boutique=form.nom_boutique.data.capitalize())
        db.session.add(ajout_boutique)
        db.session.commit()
        flash('La boutique  ({}) est ajouté  succès'.format(form.nom_boutique.data.capitalize()),'success')
        return redirect(url_for('boutique.index'))
    return render_template('boutique/ajouterb.html', title=title, form=form)



@boutique.route('/')
@login_required
@autorisation_gerant
def index():
    #Les boutiques
    title="Liste | Boutique"
    #Requete de listage des boutiques
    list_boutique=Boutique.query.all()

    return render_template('boutique/index.html', title=title, listes=list_boutique)


@boutique.route('/<int:bout_id>/boutique', methods=['GET','POST'])
@login_required
@autorisation_gerant
def editer_boutique(bout_id):

    # #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))
        
    #formulaire
    form=BoutiqueEditerForm()
    #Verification de l'existence de la boutique
    boutique_edit=Boutique.query.filter_by(id=bout_id).first_or_404()
    #Titre de la catégorie
    title=" {} | Modification "+boutique_edit.nom_boutique
    #Validation d'enregistrement
    if form.validate_on_submit():
        boutique_edit.nom_boutique=form.nom_boutique.data.capitalize()
        db.session.commit()
        flash("Modification avec succès",'success')
        return redirect(url_for('boutique.index'))
    elif request.method =='GET':
        form.nom_boutique.data=boutique_edit.nom_boutique

    return render_template('boutique/boutmod.html', title=title, form=form)

