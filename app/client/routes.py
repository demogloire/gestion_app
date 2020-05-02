from flask import render_template, flash, url_for, redirect, request, session
from .. import db
from ..models import Categorie, Produit,  Facture, Client, Typeclient
from app.client.forms import AjouterClientForm
from app.client.autorisation  import autorisation_gerant, autorisation_vendeur
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.sql import func

from . import client


@client.route('/')
@login_required
@autorisation_vendeur
def index():
    #Le clients
    title=f"Clients | {current_user.user_entreprise.denomination}"
    option_encours="client"

    cleints_dettes=db.session.query(Facture,func.sum(Facture.montant).label("sommes")).filter(Facture.dette==True, Facture.montant > 0, Facture.annule==False).group_by(Facture.client_id).order_by(Facture.id.desc()).limit(30)
    client_dispo=[] #
    client_serie=[] #Tableau de dette 

    for clien_gra in cleints_dettes:
      i=clien_gra.Facture.facture_client.nom_client
      b=round(clien_gra.sommes,2)
      client_serie.insert(0,b)
      client_dispo.insert(0,i)
    
    return render_template('client/index.html',label=client_dispo, series=client_serie, title=title, option_encours=option_encours)


@client.route('/configurations', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_conf():
    #Les catagories des articles
    title=f"Clients | {current_user.user_entreprise.denomination}"
    option_encours="client"

    client_boutique=Client.query.filter(Client.boutique_id==current_user.boutique_id, Client.nom_client !='Tous').all()

    form=AjouterClientForm()

    if form.validate_on_submit():
        client=Client(nom_client=form.nom_client.data.title(), typeclient_id=form.typeclient_id.data.id, boutique_id=current_user.boutique_id,
                      tel_client=form.tel_client.data, email=form.email.data, adresse=form.adresse.data)
        db.session.add(client)
        db.session.commit()
        flash("Vous avez enregistré un nouveau client",'success')
        return redirect(url_for('client.index_conf'))
    
    return render_template('client/index_client.html',title=title, option_encours=option_encours, listes=client_boutique, form=form)



@client.route('/configurations/<int:id>', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_conf_edit(id):
    #Les catagories des articles
    title=f"Clients | {current_user.user_entreprise.denomination}"
    option_encours="client"

    ver_client=Client.query.filter_by(id=id, boutique_id=current_user.boutique_id).first_or_404()

    if ver_client.nom_client=='Tous':
      flash("Attention (Tous) une configuration générale",'danger')

    form=AjouterClientForm()

    if form.validate_on_submit():
        ver_client.nom_client=form.nom_client.data.title()   
        ver_client.client_typeclient=form.typeclient_id.data
        ver_client.tel_client=form.tel_client.data
        ver_client.email=form.email.data
        ver_client.adresse=form.adresse.data
        db.session.commit()
        flash("Vous avez modifier les informations du client",'success')
        return redirect(url_for('client.index_conf'))
    if request.method=='GET':
      form.nom_client.data=ver_client.nom_client   
      form.typeclient_id.data=ver_client.client_typeclient
      form.tel_client.data=ver_client.tel_client
      form.email.data=ver_client.email
      form.adresse.data=ver_client.adresse
    return render_template('client/index_ed.html',title=title, option_encours=option_encours, form=form)



@client.route('/groupe/configurations/<int:id>', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_conf_cate(id):
    #Les catagories des articles
    title=f"Dette | {current_user.user_entreprise.denomination}"
    option_encours='client'
    type_client=Typeclient.query.filter_by(id=id).first_or_404()
    client_boutique=Client.query.filter(Client.boutique_id==current_user.boutique_id, Client.nom_client !='Tous', Client.typeclient_id==type_client.id).all()
    nom_type_client=type_client.nom_type
    form=AjouterClientForm()
    return render_template('client/index_client.html',title=title, nom_type_client=nom_type_client, option_encours=option_encours, listes=client_boutique, form=form)


@client.route('/dette', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_dette():
    #Les catagories des articles
    title=f"Clients | {current_user.user_entreprise.denomination}"
    option_encours="client"
    page= request.args.get('page', 1, type=int)
    cleints_dettes=db.session.query(Facture,func.sum(Facture.montant).label("sommes")).filter(Facture.dette==True, Facture.montant > 0, Facture.annule==False).group_by(Facture.client_id).order_by(Facture.montant.asc()).paginate(page=page, per_page=50)
    client_sommes=[] #Tableau de dette 
    clien_noms=[]

    for clien_gra in cleints_dettes.items:
      b=round(clien_gra.sommes,2)
      i=clien_gra.Facture.facture_client.nom_client
      client_sommes.insert(0,b)
      clien_noms.insert(0,i)

    dette_client=sum(client_sommes)
    
    return render_template('client/index_client_dette.html',series=client_sommes, label=clien_noms, title=title, option_encours=option_encours, listes=cleints_dettes, dette_client=dette_client)


@client.route('/impression/dette', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_dette_imp():
    #Les catagories des articles
    title=f"Clients | {current_user.user_entreprise.denomination}"
    cleints_dettes=db.session.query(Facture,func.sum(Facture.montant).label("sommes")).filter(Facture.dette==True, Facture.montant > 0, Facture.annule==False).group_by(Facture.client_id).order_by(Facture.montant.asc()).all()
    client_sommes=[] #Tableau de dette 
    clien_noms=[]

    for clien_gra in cleints_dettes:
      b=round(clien_gra.sommes,2)
      i=clien_gra.Facture.facture_client.nom_client
      client_sommes.insert(0,b)
      clien_noms.insert(0,i)

    dette_client=sum(client_sommes)
    
    return render_template('client/imprimerdette.html',series=client_sommes, label=clien_noms, title=title, listes=cleints_dettes, dette_client=dette_client)


@client.route('/dette/<int:id>', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_dette_client(id):
    #Les catagories des articles
    title=f"Clients | {current_user.user_entreprise.denomination}"
    option_encours="client"

    client_ver=Client.query.filter_by(id=id, boutique_id=current_user.boutique_id).first_or_404()
    cleints_dettes=db.session.query(Facture).filter(Facture.dette==True, Facture.montant > 0, Facture.annule==False, Facture.client_id==id).order_by(Facture.montant.desc()).all()
    client_sommes=[] #Tableau de dette 
    clien_noms=[]

    for clien_gra in cleints_dettes:
      b=round(clien_gra.montant,2)
      i=clien_gra.code_facture
      client_sommes.insert(0,b)
      clien_noms.insert(0,i)

    dette_client=sum(client_sommes)
    nom_client_verification=client_ver.nom_client
    
    return render_template('client/index_client_par_dette.html', id_client=client_ver.id, client_nom_clien=nom_client_verification, series=client_sommes, label=clien_noms, title=title, option_encours=option_encours, listes=cleints_dettes, dette_client=dette_client)


@client.route('/impression/dette/<int:id>', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def index_dette_client_imp(id):
    #Les catagories des articles
    title=f"Clients | {current_user.user_entreprise.denomination}"
    client_ver=Client.query.filter_by(id=id).first_or_404()
    cleints_dettes=db.session.query(Facture).filter(Facture.dette==True, Facture.montant > 0, Facture.annule==False, Facture.client_id==id).order_by(Facture.montant.desc()).all()
    client_sommes=[] #Tableau de dette 
    clien_noms=[]

    for clien_gra in cleints_dettes:
      b=round(clien_gra.montant,2)
      i=clien_gra.code_facture
      client_sommes.insert(0,b)
      clien_noms.insert(0,i)

    dette_client=sum(client_sommes)
    nom_client_verification=client_ver
    
    return render_template('client/imprimerdettec.html', client_nom_clien=nom_client_verification, series=client_sommes, label=clien_noms, title=title, listes=cleints_dettes, dette_client=dette_client)
