from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Fournisseur
from app.fournisseur.forms import FournisseurForm, FournisseurMAJForm
from app.fournisseur.autorisation  import autorisation_gerant
from flask_login import login_user, current_user, logout_user, login_required

from . import fournisseur

@fournisseur.route('/ajouter_fournisseur', methods=['GET','POST'])
@login_required
@autorisation_gerant
def ajouterfounisseur():
    #Les catagories de livre
    title="Fournisseur | Lambda Gestion"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=FournisseurForm()

    if form.validate_on_submit():
        fournisseur=Fournisseur(nom_fourn=form.nom_fourn.data.upper(), tel_fourn=form.tel_fourn.data, email=form.email.data, adresse=form.adresse.data)
        db.session.add(fournisseur)
        db.session.commit()
        flash("Ajout du fournisseur ({}) avec succès".format(form.nom_fourn.data.upper()),'success')
        #return redirect(url_for('categorie.index'))
    return render_template('fournisseur/ajouterf.html', title=title, form=form)



@fournisseur.route('/')
@login_required
@autorisation_gerant
def index():
    #Les forunisseurs de l'entreprise
    title="Fournisseur | Lambda Gestion"
    #Requete de listage des fournisseur
    list_foun=Fournisseur.query.all()

    return render_template('fournisseur/index.html', title=title, listes=list_foun)





@fournisseur.route('/<int:frnss_id>/fournisseur', methods=['GET','POST'])
@login_required
def editer_fournisseur(frnss_id):

    # #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))
    #formulaire
    form=FournisseurMAJForm()
    #Verification de l'existence du fornisseur
    fournisseur_edit=Fournisseur.query.filter_by(id=frnss_id).first_or_404()
    #Titre du fournisseur
    title=" {} | Modification "+fournisseur_edit.nom_fourn
    #Validation d'enregistrement
    if form.validate_on_submit():
        if fournisseur_edit.nom_fourn==form.nom_fourn.data.upper():
            fournisseur_edit.tel_fourn=form.tel_fourn.data
            fournisseur_edit.email=form.email.data
            fournisseur_edit.adresse=form.adresse.data
            db.session.commit()
            flash("Modification avec succès",'success')
            return redirect(url_for('fournisseur.index'))
        else:
            fournisseur_edit.nom_fourn=form.nom_fourn.data.upper()
            fournisseur_edit.tel_fourn=form.tel_fourn.data
            fournisseur_edit.email=form.email.data
            fournisseur_edit.adresse=form.adresse.data
            db.session.commit()
            flash("Modification avec succès",'success')
            return redirect(url_for('fournisseur.index'))

    elif request.method =='GET':
            form.nom_fourn.data=fournisseur_edit.nom_fourn
            form.tel_fourn.data=fournisseur_edit.tel_fourn
            form.email.data=fournisseur_edit.email
            form.adresse.data=fournisseur_edit.adresse
    return render_template('fournisseur/fournisseurd.html', title=title, form=form)

