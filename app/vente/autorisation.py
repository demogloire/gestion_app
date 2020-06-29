import os
import secrets
from flask import render_template, flash, url_for, redirect, request, session
from flask_login import login_user, current_user, login_required
from PIL import Image
from .. import create_app
from .. import db
from functools import wraps
from datetime import date, time
from ..models import Produit, Facture, Client, Typeclient, Vente, Boutique, Produitboutique


config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)


#Autorisation des vendeur
def autorisation_vendeur(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role =='Vendeur':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))       
    return wrap

#Autorisation des vendeurs et gérant
def autorisation_vendeur_gerant(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role =='Vendeur' or current_user.role=='Gérant':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))       
    return wrap

#Autorisation des vendeurs et gérant
def autorisation_gerant(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role=='Gérant':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('main.index'))       
    return wrap

#Fonction de vérification de la date
def dat_anne():
    mois_annee=[]
    annee=date.today()
    separateur=str(annee).split("-")
    annee_encours=separateur[0]
    for i in range(1,13):
        b=None
        if i <=9:
            b=f"0{i}"
        else:
            b=i
        mois=f"{annee_encours}-{b}"

        mois_annee.insert(0,mois)
    return mois_annee
    

def vente_inde(type_vente):
    #Tableau
    valeur_mensuelle=[]
    #Mois d'opértaion
    for date_annuelle in dat_anne():
        date_search='%{}%'.format(date_annuelle)
        #Liste des facture
        list_facture=None
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
   
        

        #Vente regroupé
        nombre_facture=[]
        montants=[]
        valeur=[]
        profit=[]
        #verification des liste   
        if list_facture != [] :
            for vente_regrouper in list_facture:
                nbr=vente_regrouper.code_facture
                montant=vente_regrouper.montant
                valeur_vendue=vente_regrouper.valeur_vendue
                profits=float(montant) - float(valeur_vendue)

                nombre_facture.insert(0,nbr)
                montants.insert(0,montant)
                valeur.insert(0,valeur_vendue)
                profit.insert(0,profits)
            facture={
                "periode":date_annuelle,
                "nbr_facture":len(nombre_facture),
                "montant":float(sum(montants)),
                "valeur":float(sum(valeur)),
                "profit":sum(profit),
                "type_vente":"Cash"
            }
            #Insertion dans le tableau
            valeur_mensuelle.insert(0,facture)
        else:
            pass
    return valeur_mensuelle

def vente_mensuelle(type_vente):
    #Tableau
    valeur_mensuelle=[]
    #Mois d'opértaion
    mois=date.today()
    separateur=str(mois).split("-")
    annee_encours=f"{separateur[0]}-{separateur[1]}"  
    #Verification du mois encours 
    mois_encours=None
    if separateur[1]=="01":
        mois_encours="Janvier"
    elif separateur[1]=="02":
        mois_encours="Février"
    elif separateur[1]=="03":
        mois_encours="Mars"
    elif separateur[1]=="04":
        mois_encours="Avril"
    elif separateur[1]=="05":
        mois_encours="Mai"
    elif separateur[1]=="06":
        mois_encours="Juin"
    elif separateur[1]=="07":
        mois_encours="Juillet"
    elif separateur[1]=="08":
        mois_encours="Août"
    elif separateur[1]=="09":
        mois_encours="Septembre"
    elif separateur[1]=="10":
        mois_encours="Octobre"
    elif separateur[1]=="11":
        mois_encours="Novembre"
    elif separateur[1]=="12":
        mois_encours="Décembre"


        
    annee_mois=f"{mois_encours}/{separateur[0]}" 
    date_search=f'%{annee_encours}%'

        #Liste des facture
    list_facture=None
    op=None
        #Type des vente
    if type_vente == 'Cash':
        list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
        op="Cash"
    elif type_vente =='Dette':
        list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
        op="Dette"
    elif type_vente=='Acompte':
        list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
        op="Acompte"
   
    #Vente regroupé
    nombre_facture=[]
    montants=[]
    valeur=[]
    profit=[]
    #verification des liste   
    if list_facture != [] :
        for vente_regrouper in list_facture:
            nbr=vente_regrouper.code_facture
            montant=vente_regrouper.montant
            valeur_vendue=vente_regrouper.valeur_vendue
            profits=float(montant) - float(valeur_vendue)

            nombre_facture.insert(0,nbr)
            montants.insert(0,montant)
            valeur.insert(0,valeur_vendue)
            profit.insert(0,profits)
        facture=[
            annee_mois,
            len(nombre_facture),
            float(sum(montants)),
            float(sum(valeur)),
            sum(profit),
            op,
            annee_encours
        ]
            #Insertion dans le tableau
        valeur_mensuelle.insert(0,facture)
    else:
        pass
    return valeur_mensuelle


def vente_mensuelle_detaille(type_vente, date_op=None):
    #Tableau
    valeur_mensuelle=[]
    #Mois d'opértaion
    separateur=str(date_op).split("-")
    annee_encours=f"{separateur[0]}-{separateur[1]}"  
    #Verification du mois encours 
    date_search=f'%{annee_encours}%'
    #Liste des facture
    list_facture=None
    op=None
        #Type des vente
    if type_vente == 'Cash':
        list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
        op="Cash"
    elif type_vente =='Dette':
        list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
        op="Dette"
    elif type_vente=='Acompte':
        list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
        op="Acompte"
   
    #Variable de vérification
    acomptes=None
    #verification des liste   
    if list_facture != [] :
        for vente_regrouper in list_facture:
            facture_id=vente_regrouper.id
            codefacture=vente_regrouper.code_facture
            type_facture=vente_regrouper.type_vente
            montant=vente_regrouper.montant
            valeur_vendue=vente_regrouper.valeur_vendue
            profits=float(montant) - float(valeur_vendue)
            pars=vente_regrouper.facture_user.prenom
            date_op=vente_regrouper.date

            facture=[
                facture_id,
                codefacture,
                type_facture,
                float(montant),
                float(valeur_vendue),
                float(profits),
                vente_regrouper.facture_boutique.nom_boutique,
                pars,
                date_op,
                #Pour les options de facture cash
                vente_regrouper.code_id_facture,
                vente_regrouper.liquidation
            ]
            #Insertion dans le tableau
            valeur_mensuelle.insert(0,facture)
    else:
        pass
    return valeur_mensuelle

def vente_mensuelle_detaille_boutique(type_vente, date_op, nbr_compte, boutique_requete):
    #Tableau
    valeur_mensuelle=[]
    #Mois d'opértaion
    separateur=str(date_op).split("/")
    #verification de la date
    annee_encours=None

    if nbr_compte == 10:
        annee_encours=f"{separateur[2]}-{separateur[1]}-{separateur[0]}"  
    elif nbr_compte == 7:
        annee_encours=f"{separateur[1]}-{separateur[0]}" 
    elif nbr_compte == 4:
        annee_encours=f"{date_op}" 
    #Boutique encours d'execution
    boutique_requete=boutique_requete
    #Verification du mois encours 
    date_search=f'%{annee_encours}%'
    #Liste des facture
    list_facture=None
    op=None
    
    if boutique_requete is not None:
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Acompte"
    else:
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Acompte"
    #verification des liste   
    if list_facture != [] :
        for vente_regrouper in list_facture:
            facture_id=vente_regrouper.id
            codefacture=vente_regrouper.code_facture
            type_facture=vente_regrouper.type_vente
            montant=vente_regrouper.montant
            valeur_vendue=vente_regrouper.valeur_vendue
            profits=float(montant) - float(valeur_vendue)
            pars=vente_regrouper.facture_user.prenom
            date_op=vente_regrouper.date
            

            facture=[
                facture_id,
                codefacture,
                type_facture,
                float(montant),
                float(valeur_vendue),
                float(profits),
                vente_regrouper.facture_boutique.nom_boutique,
                pars,
                date_op,
                #Pour les options de facture cash
                vente_regrouper.code_id_facture,
                vente_regrouper.liquidation


            ]
            #Insertion dans le tableau
            valeur_mensuelle.insert(0,facture)
    else:
        pass
    return valeur_mensuelle

def vente_mensuelle_triage(type_vente, date_op, nbr_compte, boutique_requete):
    #Tableau
    valeur_mensuelle=[]
    #Mois d'opértaion
    date_op=date_op
    separateur=str(date_op).split("/")
    #verification de la date
    annee_encours=None

    if nbr_compte == 10:
        annee_encours=f"{separateur[2]}-{separateur[1]}-{separateur[0]}"  
    elif nbr_compte == 7:
        annee_encours=f"{separateur[1]}-{separateur[0]}" 
    elif nbr_compte == 4:
        annee_encours=f"{date_op}" 
    #Boutique encours d'execution
    boutique_requete=None

          
    annee_mois=f"{annee_encours}" 
    date_search=f'%{annee_encours}%'

    #Liste des facture
    list_facture=None
    op=None
    
    verification_plage=None
    
    if 'verification_plage' in session:
        verification_plage=session['verification_plage']
    else:
        boutique_requete=boutique_requete
        
  
    if verification_plage is not None:
        boutique_requete=boutique_requete.id
    else:
        boutique_requete=boutique_requete
        
        
    
        
    if boutique_requete is not None:
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.date.ilike(date_search)).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.date.ilike(date_search)).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.date.ilike(date_search)).all()
            op="Acompte"
    else:
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.date.ilike(date_search)).all()
            op="Acompte"
   
    #Vente regroupé
    nombre_facture=[]
    montants=[]
    valeur=[]
    profit=[]
    #verification des liste   
    if list_facture != [] :
        for vente_regrouper in list_facture:
            nbr=vente_regrouper.code_facture
            montant=vente_regrouper.montant
            valeur_vendue=vente_regrouper.valeur_vendue
            profits=float(montant) - float(valeur_vendue)

            nombre_facture.insert(0,nbr)
            montants.insert(0,montant)
            valeur.insert(0,valeur_vendue)
            profit.insert(0,profits)
        facture=[
            annee_mois,
            len(nombre_facture),
            float(sum(montants)),
            float(sum(valeur)),
            sum(profit),
            op,
            annee_encours
        ]
            #Insertion dans le tableau
        valeur_mensuelle.insert(0,facture)
    else:
        pass
    return valeur_mensuelle

def vente_plage_detaille_boutique(type_vente, date_op_une, date_op_deux ,boutique_requete):
    #Tableau
    valeur_mensuelle=[]
    #Boutique encours d'execution
    boutique_requete=boutique_requete
    print(boutique_requete,'fdsfsdflksdjfljdsqf flkdsqfjsqdoifdsqjf fidsjfoisqjfjsqdoifsq')
    #Les dates de vérifications encours
    date_formatage_une=date_op_une
    date_formatage_deux=date_op_deux
    #Liste des facture
    list_facture=None
    op=None
    #Type des vente
    if boutique_requete is not None:
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Acompte"
    else:
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Acompte"
   
    #verification des liste   
    if list_facture != [] :
        for vente_regrouper in list_facture:
            facture_id=vente_regrouper.id
            codefacture=vente_regrouper.code_facture
            type_facture=vente_regrouper.type_vente
            montant=vente_regrouper.montant
            valeur_vendue=vente_regrouper.valeur_vendue
            profits=float(montant) - float(valeur_vendue)
            pars=vente_regrouper.facture_user.prenom
            date_op=vente_regrouper.date
            

            facture=[
                facture_id,
                codefacture,
                type_facture,
                float(montant),
                float(valeur_vendue),
                float(profits),
                vente_regrouper.facture_boutique.nom_boutique,
                pars,
                date_op,
                #Pour les options de facture cash
                vente_regrouper.code_id_facture,
                vente_regrouper.liquidation


            ]
            #Insertion dans le tableau
            valeur_mensuelle.insert(0,facture)
    else:
        pass
    return valeur_mensuelle

def vente_plage_triage(type_vente, date_op_une, date_op_deux, boutique_requete):
    #Tableau
    valeur_mensuelle=[]
    #Les dates de vérifications encours
    date_formatage_une=date_op_une
    date_formatage_deux=date_op_deux
    #Liste des facture
    list_facture=None
    
    print(boutique_requete,'sff_______________________________________fdsfsd_______________________________________')
    
    op=None
    if boutique_requete is not None:
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Acompte"
    else:
        #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Acompte"
   
    #Vente regroupé
    nombre_facture=[]
    montants=[]
    valeur=[]
    profit=[]
    #verification des liste   
    if list_facture != [] :
        for vente_regrouper in list_facture:
            nbr=vente_regrouper.code_facture
            montant=vente_regrouper.montant
            valeur_vendue=vente_regrouper.valeur_vendue
            profits=float(montant) - float(valeur_vendue)

            nombre_facture.insert(0,nbr)
            montants.insert(0,montant)
            valeur.insert(0,valeur_vendue)
            profit.insert(0,profits)
        facture=[
            True,
            len(nombre_facture),
            float(sum(montants)),
            float(sum(valeur)),
            sum(profit),
            op,
            True
        ]
            #Insertion dans le tableau
        valeur_mensuelle.insert(0,facture)
    else:
        pass
    return valeur_mensuelle

def produit_triage_mensuel(type_vente):
    
    """Cette fonction retourne un tableau de totalité des ventes par produit sur le mois encours"""
    liste_de_trie=dict()
    liste_de_valeur=dict()

    liste_finale_produit=[]
    #Mois d'opértaion
    mois=date.today()
    separateur=str(mois).split("-")
    annee_encours=f"{separateur[0]}-{separateur[1]}"  
    
    date_search=f'%{annee_encours}%'
    
    #Liste des facture
    list_facture=None
    op=None
    #Type des vente
    if type_vente == 'Cash':
        list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
        op="Cash"
    elif type_vente =='Dette':
        list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
        op="Dette"
    elif type_vente=='Acompte':
        list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
        op="Acompte"
        
    for fa in list_facture:
        for p in fa.ventes:
            if len(liste_de_trie) == 0 :
                liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, int(p.quantite), float(p.quantite)* float(p.prix_unitaire),0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]
            else:
                if p.vente_produitboutique.nom_produit in liste_de_trie:
                    quantite_nouvelle=liste_de_trie[p.vente_produitboutique.nom_produit][1] + int(p.quantite)
                    montan_nouvelle=liste_de_trie[p.vente_produitboutique.nom_produit][2] + (float(p.quantite)* float(p.prix_unitaire))
                    liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, quantite_nouvelle, montan_nouvelle,0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]
                else:
                    liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, int(p.quantite), float(p.quantite)* float(p.prix_unitaire),0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]

    for valeur in list_facture:
        for p in valeur.valeurventes:
            if len(liste_de_valeur) == 0:
                m=float(p.montants)
                liste_de_valeur[p.valeur_produitboutique.nom_produit]=[m]
            else:
                if p.valeur_produitboutique.nom_produit in liste_de_valeur:
                    liste_de_valeur[p.valeur_produitboutique.nom_produit]=[float(liste_de_valeur[p.valeur_produitboutique.nom_produit][0]) + float(p.montants)] 
                else:
                    liste_de_valeur[p.valeur_produitboutique.nom_produit]=[p.montants]
                    
    for produit_encours in liste_de_trie:
        if liste_de_trie[produit_encours][0] in liste_de_valeur:
            valeur_stock=float(liste_de_valeur[produit_encours][0])
            profit=liste_de_trie[produit_encours][2] - float(valeur_stock)
            
            p=[liste_de_trie[produit_encours][0],
                liste_de_trie[produit_encours][1],
                liste_de_trie[produit_encours][2],
                valeur_stock,
                profit,
                liste_de_trie[produit_encours][5],
                liste_de_trie[produit_encours][6],
                op]
            liste_finale_produit.insert(0,p)
    
    return liste_finale_produit

def produit_triage_par_option(type_vente, date_op, boutique, produit_prod):
    
    """Cette fonction retourne un tableau de totalité des ventes par produit sur le mois encours"""
    liste_de_trie=dict()
    liste_de_valeur=dict()
    produit_encours_triage=[]
    liste_finale_produit=[]
    #Mois d'opértaion

    
    date_search=f'%{date_op}%'
    
    #Liste des facture
    list_facture=None
    op=None
    
  
        
        
        
    if boutique is None:
         #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Acompte"
    else:
        id_boutique=boutique.id
         #Type des vente
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.boutique_id==id_boutique, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.boutique_id==id_boutique, Facture.montant>=0.001,Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.boutique_id==id_boutique, Facture.montant>=0.001, Facture.date.ilike(date_search)).order_by(Facture.id.desc()).all()
            op="Acompte"

    
    for fa in list_facture:
        for p in fa.ventes:
            if len(liste_de_trie) == 0 :
                liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, int(p.quantite), float(p.quantite)* float(p.prix_unitaire),0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]
            else:
                if p.vente_produitboutique.nom_produit in liste_de_trie:
                    quantite_nouvelle=liste_de_trie[p.vente_produitboutique.nom_produit][1] + int(p.quantite)
                    montan_nouvelle=liste_de_trie[p.vente_produitboutique.nom_produit][2] + (float(p.quantite)* float(p.prix_unitaire))
                    liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, quantite_nouvelle, montan_nouvelle,0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]
                else:
                    liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, int(p.quantite), float(p.quantite)* float(p.prix_unitaire),0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]

    for valeur in list_facture:
        for p in valeur.valeurventes:
            if len(liste_de_valeur) == 0:
                m=float(p.montants)
                liste_de_valeur[p.valeur_produitboutique.nom_produit]=[m]
            else:
                if p.valeur_produitboutique.nom_produit in liste_de_valeur:
                    liste_de_valeur[p.valeur_produitboutique.nom_produit]=[float(liste_de_valeur[p.valeur_produitboutique.nom_produit][0]) + float(p.montants)] 
                else:
                    liste_de_valeur[p.valeur_produitboutique.nom_produit]=[p.montants]
                    
    for produit_encours in liste_de_trie:
        if liste_de_trie[produit_encours][0] in liste_de_valeur:
            valeur_stock=float(liste_de_valeur[produit_encours][0])
            profit=liste_de_trie[produit_encours][2] - float(valeur_stock)
            
            liste_de_trie[produit_encours]=[liste_de_trie[produit_encours][0],
                                            liste_de_trie[produit_encours][1],
                                            liste_de_trie[produit_encours][2],
                                            valeur_stock,
                                            profit,
                                            liste_de_trie[produit_encours][5],
                                            liste_de_trie[produit_encours][6],
                                            op]
            
            
            p=[liste_de_trie[produit_encours][0],
                liste_de_trie[produit_encours][1],
                liste_de_trie[produit_encours][2],
                valeur_stock,
                profit,
                liste_de_trie[produit_encours][5],
                liste_de_trie[produit_encours][6],
                op]
            liste_finale_produit.insert(0,p)
    
    if produit_prod is not None:
        if produit_prod in liste_de_trie:
            p=[liste_de_trie[produit_prod][0],
                liste_de_trie[produit_prod][1],
                liste_de_trie[produit_prod][2],
                liste_de_trie[produit_prod][3],
                liste_de_trie[produit_prod][4],
                liste_de_trie[produit_prod][5],
                liste_de_trie[produit_prod][6],
                liste_de_trie[produit_prod][7]]
            produit_encours_triage.insert(0,p)
        return produit_encours_triage
        
    return liste_finale_produit





def vente_plage_triage_admin(type_vente, date_op, boutique_requete, produit_prod):
    """Cette fonction retourne un tableau de totalité des ventes par produit sur le mois encours"""
    #Les dates de vérifications encours
    date_formatage_une=date_op[0]
    date_formatage_deux=date_op[1]
    
    #Liste des facture
    liste_de_trie=dict()
    liste_de_valeur=dict()
    produit_encours_triage=[]
    liste_finale_produit=[]
    #Liste des facture
    list_facture=None
    op=None
    
    #Type des vente
    if boutique_requete is None:
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Acompte"
    else:
        if type_vente == 'Cash':
            list_facture=Facture.query.filter(Facture.cash==True, Facture.boutique_id==boutique_requete,  Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Cash"
        elif type_vente =='Dette':
            list_facture=Facture.query.filter(Facture.dette==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Dette"
        elif type_vente=='Acompte':
            list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.boutique_id==boutique_requete, Facture.annule==False, Facture.montant>=0.001, Facture.date.between(f'{date_formatage_une}', f'{date_formatage_deux}')).order_by(Facture.id.desc()).all()
            op="Acompte"
    
        
    for fa in list_facture:
        for p in fa.ventes:
            if len(liste_de_trie) == 0 :
                liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, int(p.quantite), float(p.quantite)* float(p.prix_unitaire),0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]
            else:
                if p.vente_produitboutique.nom_produit in liste_de_trie:
                    quantite_nouvelle=liste_de_trie[p.vente_produitboutique.nom_produit][1] + int(p.quantite)
                    montan_nouvelle=liste_de_trie[p.vente_produitboutique.nom_produit][2] + (float(p.quantite)* float(p.prix_unitaire))
                    liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, quantite_nouvelle, montan_nouvelle,0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]
                else:
                    liste_de_trie[p.vente_produitboutique.nom_produit]=[p.vente_produitboutique.nom_produit, int(p.quantite), float(p.quantite)* float(p.prix_unitaire),0,0, p.vente_produitboutique.nombre_contenu, p.vente_produitboutique.emballage]

    for valeur in list_facture:
        for p in valeur.valeurventes:
            if len(liste_de_valeur) == 0:
                m=float(p.montants)
                liste_de_valeur[p.valeur_produitboutique.nom_produit]=[m]
            else:
                if p.valeur_produitboutique.nom_produit in liste_de_valeur:
                    liste_de_valeur[p.valeur_produitboutique.nom_produit]=[float(liste_de_valeur[p.valeur_produitboutique.nom_produit][0]) + float(p.montants)] 
                else:
                    liste_de_valeur[p.valeur_produitboutique.nom_produit]=[p.montants]
                    
    for produit_encours in liste_de_trie:
        if liste_de_trie[produit_encours][0] in liste_de_valeur:
            valeur_stock=float(liste_de_valeur[produit_encours][0])
            profit=liste_de_trie[produit_encours][2] - float(valeur_stock)
            
            liste_de_trie[produit_encours]=[liste_de_trie[produit_encours][0],
                                            liste_de_trie[produit_encours][1],
                                            liste_de_trie[produit_encours][2],
                                            valeur_stock,
                                            profit,
                                            liste_de_trie[produit_encours][5],
                                            liste_de_trie[produit_encours][6],
                                            op]
            
            
            p=[liste_de_trie[produit_encours][0],
                liste_de_trie[produit_encours][1],
                liste_de_trie[produit_encours][2],
                valeur_stock,
                profit,
                liste_de_trie[produit_encours][5],
                liste_de_trie[produit_encours][6],
                op]
            liste_finale_produit.insert(0,p)
    
    if produit_prod is not None:
        if produit_prod in liste_de_trie:
            p=[liste_de_trie[produit_prod][0],
                liste_de_trie[produit_prod][1],
                liste_de_trie[produit_prod][2],
                liste_de_trie[produit_prod][3],
                liste_de_trie[produit_prod][4],
                liste_de_trie[produit_prod][5],
                liste_de_trie[produit_prod][6],
                liste_de_trie[produit_prod][7]]
            produit_encours_triage.insert(0,p)
        return produit_encours_triage
        
    return liste_finale_produit



