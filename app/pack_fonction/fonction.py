import os
import secrets
from flask import render_template, flash, url_for, redirect, request, session
from flask_login import login_user, current_user, login_required
from PIL import Image
from .. import create_app
from .. import db, vente
from functools import wraps

from ..models import Produit, Facture, Client, Typeclient, Comptes 


config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

def codefacture():
    #Verfification de l'identification de la facture
    facture_id=Facture.query.filter_by(boutique_id=current_user.boutique_id, facture_user=current_user).order_by(Facture.id.desc()).first()
    id_facture_utilisateur=None
    if facture_id is None:
        id_facture_utilisateur=1
    else:
        id_facture_utilisateur=facture_id.id+1
    codefactureuser="#{}-{}{}".format(id_facture_utilisateur, current_user.boutique_id,current_user.id) # Code de la facture
    session["codefactureuser"]=codefactureuser
    return codefactureuser

def verification_facture():
    if 'codefactureuser' in session:
        return  session["codefactureuser"]
    else:
        return False

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/produit', picture_fn)
    output_sz = (240,180)
    i= Image.open(form_picture)
    i.thumbnail(output_sz)
    i.save(picture_path)
    return picture_fn

def save_picture_produit(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/produit', picture_fn)
    output_sz = (400,300)
    i= Image.open(form_picture)
    i.thumbnail(output_sz)
    i.save(picture_path)
    return picture_fn


def codeproduit():
    #Verfification de l'identification du produit
    produi_id=Produit.query.order_by(Produit.id.desc()).first()
    id_prod=None
    if produi_id is None:
        id_prod=1
    else:
        id_prod=produi_id.id+1
    codeproduit="#{}".format(id_prod) #Code partielle du produit
    return codeproduit


def verification_de_role(role, droit_b, droit_d):
    ver="Faux"
    ver_b="Ok"
    if role=="Gérant" or role=="Associé":
        if droit_b !="Aucun" or droit_d !="Aucun":
            flash("Le Gérant ou l'Associé, ne peut être associé à un dépôt ou boutique","danger")
            return ver
        else:
            return ver_b
    if role == "Vendeur":
        if droit_b=="Aucun" and droit_d!="Aucun":
            flash("Le vendeur est associé à une boutiqe","danger")
            return ver
        else:
            return ver_b
    if role == "Magasinier":
        if droit_b!="Aucun" and droit_d=="Aucun":
            flash("Magasinier est associé à un dépôt","danger")
            return ver
        else:
            return ver_b

#Vérification du client

def client_defautl():
    #Ajout de classification des clients
    type_client=Typeclient.query.filter_by(nom_type='Normale').first()
    id_type_client=type_client
    if type_client is None:
        type_client=Typeclient(nom_type='Normale', statut=True)
        db.session.add(type_client)
        db.session.commit()
        id_type_client=type_client
    #Ajout vérificaion du client dans la base de données
    clienr='Tous'
    client_code_add=None
    client_ver=Client.query.filter_by(nom_client=clienr.title(), boutique_id=current_user.boutique_id).first()
    if client_ver is None:
        client=Client(nom_client=clienr.title(), client_typeclient=id_type_client, boutique_id=current_user.boutique_id)
        db.session.add(client)
        db.session.commit()
        client_code_add=client
    else:
        client_code_add=client_ver
    return client_code_add


def client_entree(nom):
    #Gestion des clients
    client_code_add=None
    if nom =='':
        return client_code_add
    #Ajout de classification des clients
    type_client=Typeclient.query.filter_by(nom_type='Normale').first()
    #Ajout vérificaion du client dans la base de données
    
    client_ver=Client.query.filter_by(nom_client=nom.title(), boutique_id=current_user.boutique_id).first()
    if client_ver is None:
        client=Client(nom_client=nom.title(), typeclient_id=type_client.id, boutique_id=current_user.boutique_id)
        db.session.add(client)
        db.session.commit()
        client_code_add=client
    else:
        client_code_add=client_ver
    return client_code_add

#Les identifiants de la facture du client
def id_facture_client():
    id_f=None
    if 'idfacture' in session:
        id_f=session["idfacture"]
        return id_f
    else:
        return id_f


#La date de la fecture
def facture_date():
    id_f=None
    if 'datefacture' in session:
        id_f=session["datefacture"]
        return id_f
    else:
        return id_f


#Emballage
def emballage(emballage, stock_dispo, stock_vendu):
    emb_produits=None
    if emballage !="Carton":
        if stock_dispo  == 0  and stock_vendu <=1:
            emb_produits="Pièce"
        else:
            emb_produits="Pièces"
    else:
        if stock_dispo  == 0  and stock_vendu <=1: 
            emb_produits="{}".format(emballage)
        else:
            emb_produits="{}s".format(emballage)

    return emb_produits

#Emballage du detaille
def emballage_taille(stock_dispo, stock_vendu):
    emb_produits=None
    if stock_dispo  == 0  and stock_vendu <=1:
        emb_produits="Pièce"
    else:
        emb_produits="Pièces"
    return emb_produits

#Emballage du detaille
def emballage_taille_accompte(stock_vendu):
    emb_produits=None
    if stock_vendu <=1:
        emb_produits="Pièce"
    else:
        emb_produits="Pièces"
    return emb_produits


#Validation de type facture
def validationtype():
    validation_factur=None
    if 'validation' in session:
        validation_factur=session['validation']
        if validation_factur == 0 or validation_factur == 1:
            return validation_factur
        else:
            return None
    else:
        return None


#Validation de la facture acompte
def validationacompte():
    validation_factur=None
    if 'validation_acompte' in session:
        validation_factur=session['validation_acompte']
        if validation_factur == 0 or validation_factur == 1:
            return validation_factur
        else:
            return None
    else:
        return None



#Validation de type facture
def validationtype_dette():
    vali_facture=None
    if 'validation_dette' in session:
        vali_facture=session['validation_dette']
        if vali_facture == 0 or vali_facture == 1:
            return vali_facture
        else:
            return None
        return vali_facture
    else:
        return None


#Autorisation des vendeur
def autorisation_gerant(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role =='Gérant':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))       
    return wrap

#Compte de gestion des clients
def compte_client():
    #Caisse=01, Compte bancaire=02, Client=03, Autres=04
    comptes_client=Comptes.query.filter_by(boutique_id=current_user.boutique_id).order_by(Comptes.id.desc()).first()
    numero_client=None
    code_gestion=None
    branche_gestion="03"
    if comptes_client is None:
        numero_client='001'
    else:
        numero_client=f'00{comptes_client.id + 1}'
    
    if current_user.role=='Gérant':
        code_gestion=1
    else:
        code_gestion=current_user.boutique_id
    
    compte_complet_client=f"{code_gestion} - {numero_client} - {branche_gestion}"
    
    return compte_complet_client
    

    




        












