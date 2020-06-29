import os
import secrets
from flask import render_template, flash, url_for, redirect, request, session
from flask_login import login_user, current_user, login_required
from .. import create_app
from .. import db, vente
from functools import wraps

from ..models import Produit, Stock 
#from . import user

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/user', picture_fn)
    output_sz = (240,180)
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

#Autorisation des vendeur
def autorisation_magasinier(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role =='Magasinier':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))       
    return wrap



def stock_produit_boutique():
    # Dictionnaire des données
    liste_de_produit=dict()
    # Liste de produit
    liste_produit=[]
    #Liste de requêtes de stock des produits
    stock_boutique=Stock.query.filter(Stock.produitboutique_id!=None,  Stock.solde==True).all()
    #Requête de produit 
    for stock_p in stock_boutique:
       if len(liste_de_produit) == 0:
          liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                       stock_p.stock_produitboutique.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produitboutique.emballage,
                                                                       stock_p.stock_produitboutique.nombre_contenu,
                                                                       ]
       else:
          if stock_p.stock_produitboutique.nom_produit in liste_de_produit:
             qte_produit=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][2]) + float(stock_p.disponible)
             valeur=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][3]) + float(stock_p.valeur_dispo)
             liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[liste_de_produit[stock_p.stock_produitboutique.nom_produit][0],
                                                                          liste_de_produit[stock_p.stock_produitboutique.nom_produit][1],
                                                                          qte_produit,
                                                                          valeur,
                                                                          liste_de_produit[stock_p.stock_produitboutique.nom_produit][4],
                                                                          liste_de_produit[stock_p.stock_produitboutique.nom_produit][5]]
          else:
             liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                       stock_p.stock_produitboutique.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produitboutique.emballage,
                                                                       stock_p.stock_produitboutique.nombre_contenu,
                                                                       ]
    
    for pro in liste_de_produit:
        p=[liste_de_produit[pro][0],
           liste_de_produit[pro][1],
           liste_de_produit[pro][2],
           liste_de_produit[pro][3],
           liste_de_produit[pro][4],
           liste_de_produit[pro][5]]
        liste_produit.insert(0,p)

    return liste_produit


def stock_produit_boutique_triage(boutique,produit):
    
    #Variable de requete
    stock_boutique=None
    # Dictionnaire des données
    liste_de_produit=dict()
    # Liste de produit
    liste_produit=[]
    
    # Vérification es information envoyé
    if boutique is None:
        stock_boutique=Stock.query.filter(Stock.produitboutique_id!=None,  Stock.solde==True).all()
    else:
        stock_boutique=Stock.query.filter(Stock.produitboutique_id!=None,  Stock.solde==True, Stock.boutique_id==boutique).all()
    
    #Requête de produit 
    for stock_p in stock_boutique:
       if len(liste_de_produit) == 0:
          liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                       stock_p.stock_produitboutique.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produitboutique.emballage,
                                                                       stock_p.stock_produitboutique.nombre_contenu,
                                                                       ]
       else:
          if stock_p.stock_produitboutique.nom_produit in liste_de_produit:
             qte_produit=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][2]) + float(stock_p.disponible)
             valeur=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][3]) + float(stock_p.valeur_dispo)
             liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[liste_de_produit[stock_p.stock_produitboutique.nom_produit][0],
                                                                          liste_de_produit[stock_p.stock_produitboutique.nom_produit][1],
                                                                          qte_produit,
                                                                          valeur,
                                                                          liste_de_produit[stock_p.stock_produitboutique.nom_produit][4],
                                                                          liste_de_produit[stock_p.stock_produitboutique.nom_produit][5]]
          else:
             liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                       stock_p.stock_produitboutique.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produitboutique.emballage,
                                                                       stock_p.stock_produitboutique.nombre_contenu,
                                                                       ]
    #Triage avec le produit selectioné
    if produit is not None:
        if produit in liste_de_produit:
            p=[liste_de_produit[produit][0],
                liste_de_produit[produit][1],
                liste_de_produit[produit][2],
                liste_de_produit[produit][3],
                liste_de_produit[produit][4],
                liste_de_produit[produit][5]]
            liste_produit.insert(0,p)
        return liste_produit
    
    #Renvoir des information sur le triage de la boutique
    for pro in liste_de_produit:
        p=[liste_de_produit[pro][0],
           liste_de_produit[pro][1],
           liste_de_produit[pro][2],
           liste_de_produit[pro][3],
           liste_de_produit[pro][4],
           liste_de_produit[pro][5]]
        liste_produit.insert(0,p)

    return liste_produit



def stock_produit_magasin():
    # Dictionnaire des données
    liste_de_produit=dict()
    # Liste de produit
    liste_produit=[]
    #Liste de requêtes de stock des produits
    stock_magasin=Stock.query.filter(Stock.produitboutique_id==None, Stock.produit_id!=None, Stock.depot_id !=None, Stock.solde==True).all()
    #Requête de produit 
    for stock_p in stock_magasin:
       if len(liste_de_produit) == 0:
          liste_de_produit[stock_p.stock_produit.nom_produit]=[stock_p.stock_produit.avatar,
                                                                       stock_p.stock_produit.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produit.emballage,
                                                                       stock_p.stock_produit.nombre_contenu,
                                                                       ]
       else:
          if stock_p.stock_produit.nom_produit in liste_de_produit:
             qte_produit=float(liste_de_produit[stock_p.stock_produit.nom_produit][2]) + float(stock_p.disponible)
             valeur=float(liste_de_produit[stock_p.stock_produit.nom_produit][3]) + float(stock_p.valeur_dispo)
             liste_de_produit[stock_p.stock_produit.nom_produit]=[liste_de_produit[stock_p.stock_produit.nom_produit][0],
                                                                          liste_de_produit[stock_p.stock_produit.nom_produit][1],
                                                                          qte_produit,
                                                                          valeur,
                                                                          liste_de_produit[stock_p.stock_produit.nom_produit][4],
                                                                          liste_de_produit[stock_p.stock_produit.nom_produit][5]]
          else:
             liste_de_produit[stock_p.stock_produit.nom_produit]=[stock_p.stock_produit.avatar,
                                                                       stock_p.stock_produit.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produit.emballage,
                                                                       stock_p.stock_produit.nombre_contenu,
                                                                       ]
    
    for pro in liste_de_produit:
        p=[liste_de_produit[pro][0],
           liste_de_produit[pro][1],
           liste_de_produit[pro][2],
           liste_de_produit[pro][3],
           liste_de_produit[pro][4],
           liste_de_produit[pro][5]]
        liste_produit.insert(0,p)

    return liste_produit


def stock_produit_magasin_triage(depot,produit):
    
    #Variable de requete
    stock_magasin=None
    # Dictionnaire des données
    liste_de_produit=dict()
    # Liste de produit
    liste_produit=[]
    
    # Vérification es information envoyé
    if depot is None:
        stock_magasin=Stock.query.filter(Stock.produitboutique_id==None, Stock.produit_id!=None, Stock.depot_id !=None, Stock.solde==True).all()
    else:
        stock_magasin=Stock.query.filter(Stock.depot_id==depot,Stock.solde==True).all()
   
    #Requête de produit 
    for stock_p in stock_magasin:
       if len(liste_de_produit) == 0:
          liste_de_produit[stock_p.stock_produit.nom_produit]=[stock_p.stock_produit.avatar,
                                                                       stock_p.stock_produit.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produit.emballage,
                                                                       stock_p.stock_produit.nombre_contenu,
                                                                       ]
       else:
          if stock_p.stock_produit.nom_produit in liste_de_produit:
             qte_produit=float(liste_de_produit[stock_p.stock_produit.nom_produit][2]) + float(stock_p.disponible)
             valeur=float(liste_de_produit[stock_p.stock_produit.nom_produit][3]) + float(stock_p.valeur_dispo)
             liste_de_produit[stock_p.stock_produit.nom_produit]=[liste_de_produit[stock_p.stock_produit.nom_produit][0],
                                                                          liste_de_produit[stock_p.stock_produit.nom_produit][1],
                                                                          qte_produit,
                                                                          valeur,
                                                                          liste_de_produit[stock_p.stock_produit.nom_produit][4],
                                                                          liste_de_produit[stock_p.stock_produit.nom_produit][5]]
          else:
             liste_de_produit[stock_p.stock_produit.nom_produit]=[stock_p.stock_produit.avatar,
                                                                       stock_p.stock_produit.nom_produit,
                                                                       stock_p.disponible,
                                                                       float(stock_p.valeur_dispo),
                                                                       stock_p.stock_produit.emballage,
                                                                       stock_p.stock_produit.nombre_contenu,
                                                                       ]
    #Triage avec le produit selectioné
    if produit is not None:
        if produit in liste_de_produit:
            p=[liste_de_produit[produit][0],
                liste_de_produit[produit][1],
                liste_de_produit[produit][2],
                liste_de_produit[produit][3],
                liste_de_produit[produit][4],
                liste_de_produit[produit][5]]
            liste_produit.insert(0,p)
        return liste_produit
    
    #Renvoir des information sur le triage de la boutique
    for pro in liste_de_produit:
        p=[liste_de_produit[pro][0],
           liste_de_produit[pro][1],
           liste_de_produit[pro][2],
           liste_de_produit[pro][3],
           liste_de_produit[pro][4],
           liste_de_produit[pro][5]]
        liste_produit.insert(0,p)

    return liste_produit




def pr_trie_gen(produit):
    #Liste des produits par boutique 
    liste_de_produit=dict()
    #Liste des boutiques
    liste_de_magasin=dict()
    #Produit boutique et des dépôts
    liste_de_ensemble=dict()
    #Liste de produit retournés
    liste_de_prod_trier=[]
    #Liste de requêtes de stock des produits
    stock_boutique=Stock.query.filter(Stock.produitboutique_id!=None,  Stock.solde==True).all()
    #Requête de produit 
    for stock_p in stock_boutique:
        if len(liste_de_produit) == 0:
            if stock_p.disponible > 0 :
                liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                            stock_p.stock_produitboutique.nom_produit,
                                                                            float(stock_p.disponible) / float(stock_p.stock_produitboutique.nombre_contenu),
                                                                            float(stock_p.valeur_dispo),
                                                                            stock_p.stock_produitboutique.emballage]
            else:
                liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                            stock_p.stock_produitboutique.nom_produit,
                                                                            0,
                                                                            float(stock_p.valeur_dispo),
                                                                            stock_p.stock_produitboutique.emballage]
        else:
            if stock_p.stock_produitboutique.nom_produit in liste_de_produit:
                if stock_p.disponible > 0:
                    qte_produit=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][2]) + (float(stock_p.disponible)/float(stock_p.stock_produitboutique.nombre_contenu)) 
                    valeur=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][3]) + float(stock_p.valeur_dispo)
                    liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[liste_de_produit[stock_p.stock_produitboutique.nom_produit][0],
                                                                                liste_de_produit[stock_p.stock_produitboutique.nom_produit][1],
                                                                                qte_produit,
                                                                                valeur,
                                                                                liste_de_produit[stock_p.stock_produitboutique.nom_produit][4]]
                else:
                    qte_produit=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][2]) + (0) 
                    valeur=float(liste_de_produit[stock_p.stock_produitboutique.nom_produit][3]) + float(stock_p.valeur_dispo)
                    liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[liste_de_produit[stock_p.stock_produitboutique.nom_produit][0],
                                                                                liste_de_produit[stock_p.stock_produitboutique.nom_produit][1],
                                                                                qte_produit,
                                                                                valeur,
                                                                                liste_de_produit[stock_p.stock_produitboutique.nom_produit][4]]
            else:
                if stock_p.disponible > 0 :
                    liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                                stock_p.stock_produitboutique.nom_produit,
                                                                                float(stock_p.disponible) / float(stock_p.stock_produitboutique.nombre_contenu),
                                                                                float(stock_p.valeur_dispo),
                                                                                stock_p.stock_produitboutique.emballage]
                else:
                    liste_de_produit[stock_p.stock_produitboutique.nom_produit]=[stock_p.stock_produitboutique.avatar,
                                                                                stock_p.stock_produitboutique.nom_produit,
                                                                                0,
                                                                                float(stock_p.valeur_dispo),
                                                                                stock_p.stock_produitboutique.emballage]
    #Liste de requêtes de stock des produits depot
    stock_magasin=Stock.query.filter(Stock.produitboutique_id==None, Stock.produit_id!=None, Stock.depot_id !=None, Stock.solde==True).all()
        #Requête de produit 
    for stock_p in stock_magasin:
        if len(liste_de_magasin) == 0:
            liste_de_magasin[stock_p.stock_produit.nom_produit]=[stock_p.stock_produit.avatar,
                                                                        stock_p.stock_produit.nom_produit,
                                                                        stock_p.disponible,
                                                                        float(stock_p.valeur_dispo),
                                                                        stock_p.stock_produit.emballage
                                                                        ]
        else:
            if stock_p.stock_produit.nom_produit in liste_de_magasin:
                qte_produit=float(liste_de_magasin[stock_p.stock_produit.nom_produit][2]) + float(stock_p.disponible)
                valeur=float(liste_de_magasin[stock_p.stock_produit.nom_produit][3]) + float(stock_p.valeur_dispo)
                liste_de_magasin[stock_p.stock_produit.nom_produit]=[liste_de_magasin[stock_p.stock_produit.nom_produit][0],
                                                                            liste_de_magasin[stock_p.stock_produit.nom_produit][1],
                                                                            qte_produit,
                                                                            valeur,
                                                                            liste_de_magasin[stock_p.stock_produit.nom_produit][4],
                                                                            ]
            else:
                liste_de_magasin[stock_p.stock_produit.nom_produit]=[stock_p.stock_produit.avatar,
                                                                        stock_p.stock_produit.nom_produit,
                                                                        stock_p.disponible,
                                                                        float(stock_p.valeur_dispo),
                                                                        stock_p.stock_produit.emballage,
                                                                        
                                                                        ]
        
    for magasin in liste_de_magasin:
        if magasin in liste_de_produit:
            avatar_pro=liste_de_magasin[magasin][0]
            nom_pro=liste_de_magasin[magasin][1]
            qte=float(liste_de_magasin[magasin][2]) + float(liste_de_produit[magasin][2])
            valeur=float(liste_de_magasin[magasin][3]) + float(liste_de_produit[magasin][3])
            emballage=liste_de_magasin[magasin][4]
            #Les produits dans un dictionnaire
            liste_de_ensemble[magasin]=[avatar_pro,nom_pro,qte,valeur,emballage]
        else:
            liste_de_ensemble[magasin]=[liste_de_magasin[liste_de_magasin][0],
                                        liste_de_magasin[liste_de_magasin][1],
                                        liste_de_magasin[liste_de_magasin][2],
                                        liste_de_magasin[liste_de_magasin][3],
                                        liste_de_magasin[liste_de_magasin][4]]    
    #Triage selon le produit envoyé
    if produit is not None:
        if produit in liste_de_ensemble: 
            p=[liste_de_ensemble[produit][0],
               liste_de_ensemble[produit][1],
               liste_de_ensemble[produit][2],
               liste_de_ensemble[produit][3],
               liste_de_ensemble[produit][4]]
        liste_de_prod_trier.insert(0,p)
        return liste_de_prod_trier 
    
    #Triage de tous les produits
    for pro in liste_de_ensemble: 
        p=[liste_de_ensemble[pro][0],
           liste_de_ensemble[pro][1],
           liste_de_ensemble[pro][2],
           liste_de_ensemble[pro][3],
           liste_de_ensemble[pro][4]]
        liste_de_prod_trier.insert(0,p)
        
    return liste_de_prod_trier                