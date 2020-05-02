from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Comptedepense, Depense 
from datetime import datetime, date
from app.depense.forms import CompteForm, DepenseForm
from app.depense.autorisation  import autorisation_gerant
from flask_login import login_user, current_user, logout_user, login_required

from . import depense

@depense.route('/rubrique_depense', methods=['GET','POST'])
@login_required
@autorisation_gerant
def ajouterboutique():
    #Boutique 
    title="Une rubrique depense"

    #Declaration du formulaire
    form=CompteForm()

    if form.validate_on_submit():
        rubrique_depense=form.rubrique.data.capitalize()
        branche=form.branche_depense.data
        #Vérification des données
        verification_rubrique=Comptedepense.query.filter_by(rubrique=rubrique_depense, branche_depense=branche).first()
        if verification_rubrique is None:
            ajout_depense=Comptedepense(rubrique=rubrique_depense, branche_depense=branche)
            db.session.add(ajout_depense)
            db.session.commit()
            flash("Vous avez ajouté une rubrique de depense",'success')
            return redirect(url_for('depense.index'))
        else:
            flash("Cette rubrique existe déjà dans la gestion de {} ".format(branche),'danger')
            return redirect(url_for('depense.ajouterboutique'))
    return render_template('depense/ajouterb.html', title=title, form=form)



@depense.route('/')
@login_required
@autorisation_gerant
def index():
    #Les boutiques
    title="Liste | Rubrique"
    #Requete de listage des boutiques
    list_depense=Comptedepense.query.all()

    return render_template('depense/index.html', title=title, listes=list_depense)



@depense.route('/activation/<int:id>')
@login_required
@autorisation_gerant
def activation_rubrique(id):
    #Vérification de rubrique
   rubriqu_d=Comptedepense.query.filter_by(id=id).first_or_404()
    #Vérification de l'état du statut
   if rubriqu_d.statut==True:
       rubriqu_d.statut=False        
       db.session.commit()
       flash("Vous avez désactivé la rubrique", "success")
       return redirect(url_for('depense.index'))
   else:
       rubriqu_d.statut=True
       db.session.commit()
       flash("Vous avez activé la rubrique", "success")
       return redirect(url_for('depense.index'))
   return render_template('depnses/index.html')


@depense.route('/<int:id>/rubrique', methods=['GET','POST'])
@login_required
@autorisation_gerant
def editer_rubrique(id):

    #formulaire
    form=CompteForm()
    #Verification de l'existence de la rubrique
    rubrique_edit=Comptedepense.query.filter_by(id=id).first_or_404()
    #Titre de la rubrique
    title=f" {rubrique_edit.rubrique} | Modification "
    #Validation d'enregistrement
    if form.validate_on_submit():
        rubrique_depense=form.rubrique.data.capitalize()
        branche=form.branche_depense.data
        #Vérification de la rubrique de depense
        verification_rub_edit=Comptedepense.query.filter_by(rubrique=rubrique_depense, branche_depense=branche).first()
        if verification_rub_edit is None:
            rubrique_edit.rubrique=rubrique_depense
            rubrique_edit.branche_depense=branche
            db.session.commit()
            flash("Modification avec succès",'success')
            return redirect(url_for('depense.index'))
        else:
            flash("Les informations inserées existe déjà",'danger')
            return redirect(url_for('editer_rubrique.index'))
    elif request.method =='GET':
        form.rubrique.data=rubrique_edit.rubrique
        branche=form.branche_depense.data=rubrique_edit.branche_depense

    return render_template('depense/boutmod.html', title=title, form=form)


@depense.route('/boutique', methods=['GET','POST'])
@login_required
def depenseboutique():
    #Boutique 
    title="Depense boutique"
    option_encours='depense'
    #Declaration du formulaire
    form=DepenseForm()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_formater="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if form.validate_on_submit():
        date_format_avant=form.date_op.data.split("-")
        date_format="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])
        rubrique=form.branche_depense.data.id
        description=form.description.data
        #Enregistrement de la dépense
        depense_b=Depense(description=description, montant=form.montant.data, user_id=current_user.id, date=date_format, comptedepense_id=rubrique, boutique_id=current_user.boutique_id)
        db.session.add(depense_b)
        db.session.commit()
        flash('Depense enregistrée','success')
        return redirect(url_for('depense.depenseboutique'))
    if request.method=='GET':
        form.date_op.data=date_formater
    
    page= request.args.get('page', 1, type=int)
    liste=Depense.query.filter_by(boutique_id=current_user.boutique_id).order_by(Depense.id.desc()).paginate(page=page, per_page=50)


    return render_template('depense/depense_boutique.html', title=title, form=form, option_encours=option_encours, listes=liste)
