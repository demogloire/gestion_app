from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Boutique, Comptes, Operation
from app.comptes.forms import CompteClientForm, CompteEditerForm, RechercheForm, OperationForm
from app.comptes.autorisation  import autorisation_vendeur
import app.pack_fonction.fonction as utilitaire
from flask_login import login_user, current_user, logout_user, login_required

from . import comptes

@comptes.route('/<int:id>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def majcompteclient(id):
    #Boutique 
    title=f"Compte | {current_user.user_entreprise.denomination}"
    option_encours="client"
    #Declaration du formulaire
    form=CompteEditerForm()
    ver_compte=Comptes.query.filter_by(id=id).first_or_404()

    if form.validate_on_submit():
        ver_compte.compte=form.nom_compte.data.title()
        db.session.commit()
        flash(f"La modification du {ver_compte.num_compte} avec success", "success")
        return redirect(url_for('compte.index'))

    if request.method=='GET':
        form.nom_compte.data=ver_compte.compte

    return render_template('comptes/ajouterc.html', option_encours=option_encours, title=title, form=form, compte=ver_compte.num_compte)



@comptes.route('/',  methods=['GET','POST'])
@login_required
@autorisation_vendeur
def index():
    title=f"Compte | {current_user.user_entreprise.denomination}"
    option_encours="client"
    #Requete de listage des boutiques
    list_compte=Comptes.query.filter_by(boutique_id=current_user.boutique_id).all()
    form=CompteClientForm()
    rech=RechercheForm()
    if form.validate_on_submit():
        c=utilitaire.compte_client()
        compte_ajouter=Comptes(num_compte=c, compte=form.nom_compte.data.title(), branche_compte=form.branche_compte.data, user_id=current_user.id, boutique_id=current_user.boutique_id,client_id=form.clients.data.id )
        db.session.add(compte_ajouter)
        db.session.commit()
        flash("Le compte {} est crée avec succès".format(c),'success')
        return redirect(url_for('compte.index'))
    
    control_filter="Vide"
    client_compte=None
    if rech.validate_on_submit():
        client_compte=Comptes.query.filter_by(num_compte=rech.clients_client.data.num_compte).first()
        control_filter="NoVide"
    
    solde_gen = []

    for sld in list_compte:
        if sld.solde is None:
            i=0
        else:
            i=sld.solde
        solde_gen.insert(0,i)
    sommes_du=sum(solde_gen)
    

    return render_template('comptes/index.html',sommes=sommes_du, rech=rech, control_filter=control_filter, client_compte=client_compte, title=title, option_encours=option_encours, listes=list_compte, form=form)


@comptes.route('/details/<int:id>',  methods=['GET','POST'])
@login_required
@autorisation_vendeur
def details(id):
    title=f"Details compte | {current_user.user_entreprise.denomination}"
    option_encours="client"

    form=OperationForm()
    ver_compte=Comptes.query.filter_by(id=id).first_or_404()
    #Requete de listage des boutiques
    list_operation=Operation.query.filter_by(compte_id=id).all()


    if form.validate_on_submit():
        #Enregistrement de l'opération
        solde_encours=None
        if ver_compte.solde is None  and str(form.type_transaction.data) =='Retrait':
            flash('Votre solde est Zéro USD', 'danger')
            return redirect(url_for('compte.details', id=id))

        elif ver_compte.solde==0  and str(form.type_transaction.data) =='Retrait':
            flash('Votre solde est Zéro USD', 'danger')
            return redirect(url_for('compte.details', id=id))

        elif ver_compte.solde is  None  and form.type_transaction.data=='Dépôt':
            solde_encours= 0 + float(form.montant.data)

        elif  ver_compte.solde >=0  and form.type_transaction.data=='Dépôt':
            solde_encours=float(ver_compte.solde) + float(form.montant.data)
        
        elif ver_compte.solde is not None or ver_compte.solde>=0 and form.type_transaction.data=='Retrait':
            if float(ver_compte.solde) >= float(form.montant.data):
                solde_encours=float(ver_compte.solde) - float(form.montant.data)
            else:
                flash("Votre solde est inferieur au montant de l'opération de retrait ", 'danger')
                return redirect(url_for('compte.details', id=id))

        date_no_formater=str(form.date_op.data)
        date_format_avant=date_no_formater.split("/")
        date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée
        insert_operation=Operation(motif=form.description.data, montant=form.montant.data, type_transanction=form.type_transaction.data,
                                    compte_id=id, date=date_operation)
        db.session.add(insert_operation)
        ver_compte.solde=solde_encours
        db.session.commit()
        flash(f'Opération de {form.type_transaction.data} éffectué avec succès', 'success')
        return redirect(url_for('compte.details', id=id))
    return render_template('comptes/comptes.html', title=title, ver_compte=ver_compte, option_encours=option_encours, listes=list_operation, form=form)


@comptes.route('/impression/clients/<int:id>',  methods=['GET','POST'])
@login_required
@autorisation_vendeur
def impdetails(id):
    title=f"Details compte | {current_user.user_entreprise.denomination}"
    option_encours="client"
    ver_compte=Comptes.query.filter_by(id=id).first_or_404()
    #Requete de listage des boutiques
    list_operation=Operation.query.filter_by(compte_id=id).all()
    return render_template('comptes/releve.html', title=title, ver_compte=ver_compte, option_encours=option_encours, listes=list_operation)



@comptes.route('/imp',  methods=['GET','POST'])
@login_required
@autorisation_vendeur
def index_imp():
    title=f"Compte | {current_user.user_entreprise.denomination}"
     #Requete de listage des boutiques
    list_compte=Comptes.query.filter_by(boutique_id=current_user.boutique_id).all()

    solde_gen = []

    for sld in list_compte:
        if sld.solde is None:
            i=0
        else:
            i=sld.solde
        solde_gen.insert(0,i)
    sommes_du=sum(solde_gen)


    return render_template('comptes/soldegen.html', title=title, listes=list_compte, sommes=sommes_du)
