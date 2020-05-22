from flask import render_template, flash, url_for, redirect, request, session, abort
from .. import db
from datetime import date, datetime
from ..models import Categorie, Produit,  Facture, Client, Typeclient, Produitboutique, Stock
from app.inventaire.forms import CorrectionForm
from app.inventaire.autorisation  import autorisation_gerant, autorisation_vendeur, autorisation_maganisier
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.sql import func

from . import inventaire


@inventaire.route('/')
@login_required
@autorisation_vendeur
def index():
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"
    produit_non_perrisable=[] #Les id des opértaions
    produit_perrisable_encours=[]
    donnees_produits=[] # Les données de tous les produits
    produits_anterieur=[]
    les_produits_inventaire=Produitboutique.query.all()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])

    # Date de l'inventaire
    date_an="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if les_produits_inventaire != []:
        for prod_encours in les_produits_inventaire:
            if prod_encours.perissable==True:
                b=prod_encours.id
                produit_perrisable_encours.insert(0,b)
            else:
                b=prod_encours.id
                produit_non_perrisable.insert(0,b)
        #LES PRODUITS PERRISSABLES
        if len(produit_perrisable_encours) > 1:
            for n in range(len(produit_perrisable_encours)):
                pro_per_sel=produit_perrisable_encours[n]
                #Selection produit encours
                inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
                #Les elements du produits
                if inv_prod_solde is not None:
                    nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                    id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                    image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                    emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                    contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                    #Stock disponible totale
                    disponible_totale=inv_prod_solde.disponible
                    inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
                    # Les produits antérieurs
                    for prod_ant_par_produi in inv_produit_anterieur:
                        i=prod_ant_par_produi.id
                        produits_anterieur.insert(0,i)
                    #Vérification si les deux produit recement stock sont là
                    if len(produits_anterieur) > 1 :
                        stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                        prix=stc.prix_unit
                        stock_mouvement=stc.quantite
                        #Difference du stock
                        diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                        if diff_stock_mouvement >=  1:
                            
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                            stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                            sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                        else:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            sommes_valeur= disponible_totale * float(prix)
                            prix_valeur=float(prix)
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                            donnees_produits.insert(0,insertion_des_donnees)

                    elif len(produits_anterieur) == 1:
                        
                        stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                        prix=stc.prix_unit
                        stock_mouvement=stc.quantite
                        #Difference du stock
                        diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                        if diff_stock_mouvement >=  1:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                            sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                        else:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            sommes_valeur= stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                    else:

                        stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/inv_prod_solde.disponible
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                        donnees_produits.insert(0,insertion_des_donnees)
        elif len(produit_perrisable_encours) == 1:

            pro_per_sel=produit_perrisable_encours[0]
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
            #Les elements du produits
            if inv_prod_solde is not None:
                nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                #Stock disponible totale
                disponible_totale=inv_prod_solde.disponible
                inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
                # Les produits antérieurs
                for prod_ant_par_produi in inv_produit_anterieur:
                    i=prod_ant_par_produi.id
                    produits_anterieur.insert(0,i)
                #Vérification si les deux produit recement stock sont là
                if len(produits_anterieur) > 1 :
                    stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                    prix=stc.prix_unit
                    stock_mouvement=stc.quantite
                    #Difference du stock
                    diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                    if diff_stock_mouvement >=  1:
                            
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                        stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                        sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                    else:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)

                elif len(produits_anterieur) == 1:

                    stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                    prix=stc.prix_unit
                    stock_mouvement=stc.quantite
                    #Difference du stock
                    diff_stock_mouvement=disponible_totale - stock_mouvement
                    #difference du stock apres le dernier approvissionnement
                    if diff_stock_mouvement >=  1:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                        sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                    else:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/inv_prod_solde.disponible
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
        #LES PRODUITS NON PERSSISABLE

        if len(produit_non_perrisable) > 1:
            for n in range(len(produit_non_perrisable)):
                pro_per_sel=produit_non_perrisable[n]
                #Selection produit encours
                inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
                #Les elements du produits
                if inv_prod_solde is not None:
                    nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                    id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                    image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                    emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                    contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                    #Stock disponible totale
                    disponible_totale=inv_prod_solde.disponible
                    sommes_valeur=float(inv_prod_solde.valeur_dispo)
                    prix_valeur= float(sommes_valeur) / float(disponible_totale)
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
        elif len(produit_non_perrisable) == 1:
            pro_per_sel=produit_non_perrisable[0]
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
            #Les elements du produits
            if inv_prod_solde is not None:
                nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                #Stock disponible totale
                disponible_totale=inv_prod_solde.disponible
                sommes_valeur=float(inv_prod_solde.valeur_dispo)
                prix_valeur= float(sommes_valeur) / float(disponible_totale)
                insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
                donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
                
    sommes_totale_evaluation=[]
    #Valeur totale de la marchandise
    for i in donnees_produits:
        b=i[5]
        sommes_totale_evaluation.insert(0,b)
    retour_somme=sum(sommes_totale_evaluation)

    return render_template('inventaire/index.html',date_in=date_an, title=title, option_encours=option_encours, inventaire=donnees_produits, valeur=retour_somme)

@inventaire.route('/options')
@login_required
@autorisation_vendeur
def conf_index():
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"

    stock_graphe=Stock.query.filter(Stock.boutique_id==current_user.boutique_id,Stock.produitboutique_id!=None,  Stock.solde==True).all()
    produit_dispo=[] #
    serie_produit=[] #Tableau valeur vendue

    for stock_pro in stock_graphe:
      i=stock_pro.disponible
      b=stock_pro.stock_produitboutique.nom_produit
      serie_produit.insert(0,i)
      produit_dispo.insert(0,b)
                

    return render_template('inventaire/conf_inve.html',title=title, option_encours=option_encours, label=produit_dispo, series=serie_produit)


@inventaire.route('/impression/produits')
@login_required
@autorisation_vendeur
def index_impr():
     #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"
    produit_non_perrisable=[] #Les id des opértaions
    produit_perrisable_encours=[]
    donnees_produits=[] # Les données de tous les produits
    produits_anterieur=[]
    les_produits_inventaire=Produitboutique.query.all()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])

    # Date de l'inventaire
    date_an="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if les_produits_inventaire != []:
        for prod_encours in les_produits_inventaire:
            if prod_encours.perissable==True:
                b=prod_encours.id
                produit_perrisable_encours.insert(0,b)
            else:
                b=prod_encours.id
                produit_non_perrisable.insert(0,b)
        #LES PRODUITS PERRISSABLES
        if len(produit_perrisable_encours) > 1:
            for n in range(len(produit_perrisable_encours)):
                pro_per_sel=produit_perrisable_encours[n]
                #Selection produit encours
                inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
                #Les elements du produits
                if inv_prod_solde is not None:
                    nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                    id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                    image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                    emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                    contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                    #Stock disponible totale
                    disponible_totale=inv_prod_solde.disponible
                    inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
                    # Les produits antérieurs
                    for prod_ant_par_produi in inv_produit_anterieur:
                        i=prod_ant_par_produi.id
                        produits_anterieur.insert(0,i)
                    #Vérification si les deux produit recement stock sont là
                    if len(produits_anterieur) > 1 :
                        stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                        prix=stc.prix_unit
                        stock_mouvement=stc.quantite
                        #Difference du stock
                        diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                        if diff_stock_mouvement >=  1:
                            
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                            stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                            sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                        else:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            sommes_valeur= disponible_totale * float(prix)
                            prix_valeur=float(prix)
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                            donnees_produits.insert(0,insertion_des_donnees)

                    elif len(produits_anterieur) == 1:
                        
                        stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                        prix=stc.prix_unit
                        stock_mouvement=stc.quantite
                        #Difference du stock
                        diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                        if diff_stock_mouvement >=  1:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                            sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                        else:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            sommes_valeur= stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                    else:

                        stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/inv_prod_solde.disponible
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                        donnees_produits.insert(0,insertion_des_donnees)
        elif len(produit_perrisable_encours) == 1:

            pro_per_sel=produit_perrisable_encours[0]
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
            #Les elements du produits
            if inv_prod_solde is not None:
                nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                #Stock disponible totale
                disponible_totale=inv_prod_solde.disponible
                inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
                # Les produits antérieurs
                for prod_ant_par_produi in inv_produit_anterieur:
                    i=prod_ant_par_produi.id
                    produits_anterieur.insert(0,i)
                #Vérification si les deux produit recement stock sont là
                if len(produits_anterieur) > 1 :
                    stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                    prix=stc.prix_unit
                    stock_mouvement=stc.quantite
                    #Difference du stock
                    diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                    if diff_stock_mouvement >=  1:
                            
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                        stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                        sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                    else:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)

                elif len(produits_anterieur) == 1:

                    stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                    prix=stc.prix_unit
                    stock_mouvement=stc.quantite
                    #Difference du stock
                    diff_stock_mouvement=disponible_totale - stock_mouvement
                    #difference du stock apres le dernier approvissionnement
                    if diff_stock_mouvement >=  1:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                        sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                    else:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/inv_prod_solde.disponible
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
        #LES PRODUITS NON PERSSISABLE

        if len(produit_non_perrisable) > 1:
            for n in range(len(produit_non_perrisable)):
                pro_per_sel=produit_non_perrisable[n]
                #Selection produit encours
                inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
                #Les elements du produits
                if inv_prod_solde is not None:
                    nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                    id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                    image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                    emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                    contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                    #Stock disponible totale
                    disponible_totale=inv_prod_solde.disponible
                    sommes_valeur=float(inv_prod_solde.valeur_dispo)
                    prix_valeur= float(sommes_valeur) / float(disponible_totale)
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
        elif len(produit_non_perrisable) == 1:
            pro_per_sel=produit_non_perrisable[0]
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first()
            #Les elements du produits
            if inv_prod_solde is not None:
                nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
                id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
                image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
                emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
                contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
                #Stock disponible totale
                disponible_totale=inv_prod_solde.disponible
                sommes_valeur=float(inv_prod_solde.valeur_dispo)
                prix_valeur= float(sommes_valeur) / float(disponible_totale)
                insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
                donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
                
    sommes_totale_evaluation=[]
    #Valeur totale de la marchandise
    for i in donnees_produits:
        b=i[5]
        sommes_totale_evaluation.insert(0,b)
    retour_somme=sum(sommes_totale_evaluation)

    return render_template('inventaire/imprimerinve.html',date_in=date_an, title=title, inventaire=donnees_produits, valeur=retour_somme)

@inventaire.route('/produit/<int:id>')
@login_required
@autorisation_vendeur
def inventaire_produit(id):
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    produit_non_perrisable=None #Les id des opértaions
    produit_perrisable_encours=None
    donnees_produits=[] # Les données de tous les produits
    produits_anterieur=[]
    les_produits_inventaire=Produitboutique.query.filter_by(id=id).first_or_404()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])

    # Date de l'inventaire
    date_an="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if les_produits_inventaire is not None:

        if les_produits_inventaire.perissable==True:
            produit_perrisable_encours=les_produits_inventaire.id
        else:
            produit_non_perrisable=les_produits_inventaire.id
                 
        if produit_perrisable_encours is not None:
            pro_per_sel=produit_perrisable_encours
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first_or_404()
            #Les elements du produits
            nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
            id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
            image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
            emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
            contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
            #Stock disponible totale
            disponible_totale=inv_prod_solde.disponible
            inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
            
            # Les produits antérieurs
            for prod_ant_par_produi in inv_produit_anterieur:
                i=prod_ant_par_produi.id
                produits_anterieur.insert(0,i)
            #Vérification si les deux produit recement stock sont là
            if len(produits_anterieur) > 1 :
                stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                prix=stc.prix_unit
                stock_mouvement=stc.quantite
                #Difference du stock
                diff_stock_mouvement=disponible_totale - stock_mouvement
                    #difference du stock apres le dernier approvissionnement
                if diff_stock_mouvement >=  1:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                    stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                    sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)

            elif len(produits_anterieur) == 1:
               
                stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                prix=stc.prix_unit
                stock_mouvement=stc.quantite
                #Difference du stock
                diff_stock_mouvement=disponible_totale - stock_mouvement
                #difference du stock apres le dernier approvissionnement
                if diff_stock_mouvement >=  1:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                    sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    sommes_valeur= disponible_totale * float(prix)
                    prix_valeur=float(prix)
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
            else:
                
                stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                sommes_valeur= stoc_valeur_enregistre
                prix_valeur=sommes_valeur/inv_prod_solde.disponible
                insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
        #LES PRODUITS NON PERSSISABLE
        if produit_non_perrisable is not None:
            pro_per_sel=produit_non_perrisable
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first_or_404()
            #Les elements du produits
            nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
            id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
            image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
            emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
            contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
            #Stock disponible totale
            inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).first()
            disponible_totale=inv_prod_solde.disponible
            sommes_valeur=float(inv_prod_solde.disponible) * float(inv_produit_anterieur.prix_unit)
            prix_valeur= float(inv_produit_anterieur.prix_unit)
            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
            donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
    #Liste des opérations de l'inventaire
    voir_operation=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==id, Stock.boutique_id==current_user.boutique_id).order_by(Stock.id.asc()).all()
          
    sommes_totale_evaluation=[]
    #Valeur totale de la marchandise
    for i in donnees_produits:
        b=i[5]
        sommes_totale_evaluation.insert(0,b)
    retour_somme=sum(sommes_totale_evaluation)

    

    return render_template('inventaire/inventaire_produit.html',produits=les_produits_inventaire, date_in=date_an, listes=voir_operation, title=title, inventaire=donnees_produits, valeur=retour_somme)

@inventaire.route('/impression/produit/<int:id>')
@login_required
@autorisation_vendeur
def imp_inventaire_produit(id):
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    produit_non_perrisable=None #Les id des opértaions
    produit_perrisable_encours=None
    donnees_produits=[] # Les données de tous les produits
    produits_anterieur=[]
    les_produits_inventaire=Produitboutique.query.filter_by(id=id).first_or_404()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])

    # Date de l'inventaire
    date_an="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if les_produits_inventaire is not None:

        if les_produits_inventaire.perissable==True:
            produit_perrisable_encours=les_produits_inventaire.id
        else:
            produit_non_perrisable=les_produits_inventaire.id
                 
        if produit_perrisable_encours is not None:
            pro_per_sel=produit_perrisable_encours
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first_or_404()
            #Les elements du produits
            nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
            id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
            image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
            emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
            contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
            #Stock disponible totale
            disponible_totale=inv_prod_solde.disponible
            inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
            # Les produits antérieurs
            for prod_ant_par_produi in inv_produit_anterieur:
                i=prod_ant_par_produi.id
                produits_anterieur.insert(0,i)
            #Vérification si les deux produit recement stock sont là
            if len(produits_anterieur) > 1 :
                stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                prix=stc.prix_unit
                stock_mouvement=stc.quantite
                #Difference du stock
                diff_stock_mouvement=disponible_totale - stock_mouvement
                    #difference du stock apres le dernier approvissionnement
                if diff_stock_mouvement >=  1:
                        
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                    stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                    sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)

            elif len(produits_anterieur) == 1:

                stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                prix=stc.prix_unit
                stock_mouvement=stc.quantite
                #Difference du stock
                diff_stock_mouvement=disponible_totale - stock_mouvement
                #difference du stock apres le dernier approvissionnement
                if diff_stock_mouvement >=  1:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                    sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
            else:
                stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                sommes_valeur= stoc_valeur_enregistre
                prix_valeur=sommes_valeur/inv_prod_solde.disponible
                insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
        #LES PRODUITS NON PERSSISABLE
        if produit_non_perrisable is not None:
            pro_per_sel=produit_non_perrisable
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produitboutique_id==pro_per_sel, Stock.solde==True).first_or_404()
            #Les elements du produits
            nom_produit_inventaire=inv_prod_solde.stock_produitboutique.nom_produit
            id_produit_inventaire=inv_prod_solde.stock_produitboutique.id
            image_produit_inventaire=inv_prod_solde.stock_produitboutique.avatar
            emballage_produit_inventaire=inv_prod_solde.stock_produitboutique.emballage
            contenue_produit_inventaire=inv_prod_solde.stock_produitboutique.nombre_contenu
            #Stock disponible totale
            inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).first()
            disponible_totale=inv_prod_solde.disponible
            sommes_valeur=float(inv_prod_solde.disponible) * float(inv_produit_anterieur.prix_unit)
            prix_valeur= float(inv_produit_anterieur.prix_unit)
            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
            donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
    #Liste des opérations de l'inventaire
    voir_operation=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produitboutique_id==id).order_by(Stock.id.asc()).all()
    
    
                
    sommes_totale_evaluation=[]
    #Valeur totale de la marchandise
    for i in donnees_produits:
        b=i[5]
        sommes_totale_evaluation.insert(0,b)
    retour_somme=sum(sommes_totale_evaluation)

    return render_template('inventaire/imprimerpro.html',produits=les_produits_inventaire, date_in=date_an, listes=voir_operation, title=title, inventaire=donnees_produits, valeur=retour_somme)


@inventaire.route('/correction/produit', methods=['POST','GET'])
@login_required
@autorisation_vendeur
def correction_produit():
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    produit_non_perrisable=None #Les id des opértaions
    produit_perrisable_encours=None
    produits_anterieur=[]
    mvment=None
    #Formulaire de correction des quantités en stock
    form=CorrectionForm()

    if form.validate_on_submit():
        data=form.produit_correct.data #Les données du produits
        #ID du produit encours de coorection
        id_produit=data.id
        corretion_stock=Produitboutique.query.filter_by(id=id_produit).first_or_404()
        #Vérification de type du produit
        if corretion_stock.perissable == True:
            produit_perrisable_encours=corretion_stock.id
        else:
            produit_non_perrisable=corretion_stock.id
        
        #Les produits perrisable
        if produit_perrisable_encours is not None:
            #Vérification des solde
            inv_prod_solde=Stock.query.filter(Stock.produitboutique_id==id_produit, Stock.solde==True).first_or_404()
            inv_produit_anterieur=Stock.query.filter(Stock.produitboutique_id==id_produit, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)

            # Les produits antérieurs
            for prod_ant_par_produi in inv_produit_anterieur:
                i=prod_ant_par_produi.id
                produits_anterieur.insert(0,i)
            #Vérifictaion de nombre de provision

            if len(produits_anterieur) > 1:
                inv_prod_ver=Stock.query.filter(Stock.id==produits_anterieur[1]).first()
                prix_unit_correction=float(inv_prod_ver.prix_unit)
                quantite_disponible=int(inv_prod_solde.disponible)
                qte_exact_de_correction=None
                disponible_corrige=None
                valeur_disponible=None
                #Réajustement de la quantité
                quantite_reasjuster=int(form.quantite.data)
                inv_prod_solde.solde=False
                #La valeur de produit
                valeur_produit=None
                #Vérification des quantités à la hausse ou soit à la basse
                if quantite_reasjuster > quantite_disponible:
                    mvment=True
                    qte_exact_de_correction=quantite_reasjuster - quantite_disponible
                    valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                    disponible_corrige=quantite_disponible + qte_exact_de_correction
                    valeur_disponible= float(inv_prod_solde.valeur_dispo) + valeur_produit 
                    
                elif quantite_reasjuster < quantite_disponible:
                    mvment=False
                    qte_exact_de_correction= quantite_disponible - quantite_reasjuster
                    valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                    disponible_corrige=quantite_disponible - qte_exact_de_correction
                    valeur_disponible= float(inv_prod_solde.valeur_dispo) - valeur_produit 
                else:
                    flash("Le stock est conforme après inventaire","danger")
                    #return redirect(url_for('inventaire.'))

                #Enregistrement des quantité corrigé à hausse
                stockage_boutique=Stock(quantite=qte_exact_de_correction , valeur=valeur_produit, datest=date.today(),
                        prix_unit=prix_unit_correction, disponible=disponible_corrige, valeur_dispo=valeur_disponible, correction=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit, solde=True, qte_correction=inv_prod_solde.disponible, 
                        valeur_correction=inv_prod_solde.valeur_dispo, mvment=mvment)
                db.session.add(stockage_boutique)
            elif len(produits_anterieur) == 1:
                inv_prod_ver=Stock.query.filter(Stock.id==produits_anterieur[0]).first()
                prix_unit_correction=float(inv_prod_ver.prix_unit)
                quantite_disponible=int(inv_prod_solde.disponible)
                qte_exact_de_correction=None
                disponible_corrige=None
                valeur_disponible=None
                #Réajustement de la quantité
                quantite_reasjuster=int(form.quantite.data)
                inv_prod_solde.solde=False
                #La valeur de produit
                valeur_produit=None
                #Vérification des quantités à la hausse ou soit à la basse
                if quantite_reasjuster > quantite_disponible:
                    mvment=True
                    qte_exact_de_correction=quantite_reasjuster - quantite_disponible
                    valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                    disponible_corrige=quantite_disponible + qte_exact_de_correction
                    valeur_disponible= float(inv_prod_solde.valeur_dispo) + valeur_produit 
                    
                elif quantite_reasjuster < quantite_disponible:
                    mvment=False
                    qte_exact_de_correction= quantite_disponible - quantite_reasjuster
                    valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                    disponible_corrige=quantite_disponible - qte_exact_de_correction
                    valeur_disponible= float(inv_prod_solde.valeur_dispo) - valeur_produit 
                else:
                    flash("Le stock est conforme après inventaire","danger")
                    #return redirect(url_for('inventaire.'))

                #Enregistrement des quantité corrigé à hausse
                stockage_boutique=Stock(quantite=qte_exact_de_correction , valeur=valeur_produit, datest=date.today(),
                        prix_unit=prix_unit_correction, disponible=disponible_corrige, valeur_dispo=valeur_disponible, correction=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit, solde=True, qte_correction=inv_prod_solde.disponible, 
                        valeur_correction=inv_prod_solde.valeur_dispo, mvment=mvment)
                db.session.add(stockage_boutique)
            elif len(produits_anterieur) == 0:
                inv_prod_ver=Stock.query.filter(Stock.produitboutique_id==id_produit, Stock.stockage==True, Stock.solde==True).first()
                prix_unit_correction=float(inv_prod_ver.prix_unit)
                quantite_disponible=int(inv_prod_solde.disponible)
                qte_exact_de_correction=None
                disponible_corrige=None
                valeur_disponible=None
                #Réajustement de la quantité
                quantite_reasjuster=int(form.quantite.data)
                inv_prod_solde.solde=False
                #La valeur de produit
                valeur_produit=None
                #Vérification des quantités à la hausse ou soit à la basse
                if quantite_reasjuster > quantite_disponible:
                    mvment=True
                    qte_exact_de_correction=quantite_reasjuster - quantite_disponible
                    valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                    disponible_corrige=quantite_disponible + qte_exact_de_correction
                    valeur_disponible= float(inv_prod_solde.valeur_dispo) + valeur_produit 
                    
                elif quantite_reasjuster < quantite_disponible:
                    mvment=False
                    qte_exact_de_correction= quantite_disponible - quantite_reasjuster
                    valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                    disponible_corrige=quantite_disponible - qte_exact_de_correction
                    valeur_disponible= float(inv_prod_solde.valeur_dispo) - valeur_produit 
                else:
                    flash("Le stock est conforme après inventaire","danger")
                    return redirect(url_for('inventaire.index_correct'))

                #Enregistrement des quantité corrigé à hausse
                stockage_boutique=Stock(quantite=qte_exact_de_correction , valeur=valeur_produit, datest=date.today(),
                        prix_unit=prix_unit_correction, disponible=disponible_corrige, valeur_dispo=valeur_disponible, correction=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit, solde=True, qte_correction=inv_prod_solde.disponible, 
                        valeur_correction=inv_prod_solde.valeur_dispo, mvment=mvment)
                db.session.add(stockage_boutique)
        #Produit non perrisable
        if produit_non_perrisable is not None:
            #Vérification des solde
            inv_prod_solde=Stock.query.filter(Stock.produitboutique_id==id_produit, Stock.solde==True).first_or_404()
            inv_produit_anterieur=Stock.query.filter(Stock.produitboutique_id==id_produit, Stock.stockage==True).order_by(Stock.id.desc()).first()
            prix_unit_correction=float(inv_produit_anterieur.prix_unit)
            quantite_disponible=int(inv_prod_solde.disponible)
            qte_exact_de_correction=None
            disponible_corrige=None
            valeur_disponible=None
            #Réajustement de la quantité
            quantite_reasjuster=int(form.quantite.data)
            inv_prod_solde.solde=False
            #La valeur de produit
            valeur_produit=None
            #Vérification des quantités à la hausse ou soit à la basse
            if quantite_reasjuster > quantite_disponible:
                mvment=True
                qte_exact_de_correction=quantite_reasjuster - quantite_disponible
                valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                disponible_corrige=quantite_disponible + qte_exact_de_correction
                valeur_disponible= float(inv_prod_solde.valeur_dispo) + valeur_produit 
                    
            elif quantite_reasjuster < quantite_disponible:
                mvment=False
                qte_exact_de_correction= quantite_disponible - quantite_reasjuster
                valeur_produit=float(qte_exact_de_correction) * prix_unit_correction
                disponible_corrige=quantite_disponible - qte_exact_de_correction
                valeur_disponible= float(inv_prod_solde.valeur_dispo) - valeur_produit 
            else:
                flash("Le stock est conforme après inventaire","danger")
                return redirect(url_for('inventaire.index_correct'))
            #Enregistrement des quantité corrigé à hausse
            stockage_boutique=Stock(quantite=qte_exact_de_correction , valeur=valeur_produit, datest=date.today(),
                prix_unit=prix_unit_correction, disponible=disponible_corrige, valeur_dispo=valeur_disponible, correction=True, boutique_id=current_user.boutique_id, 
                stock_user=current_user, produitboutique_id=id_produit, solde=True, qte_correction=inv_prod_solde.disponible, 
                valeur_correction=inv_prod_solde.valeur_dispo, mvment=mvment)
            db.session.add(stockage_boutique)
            db.session.commit()
        db.session.commit()      
        flash("La correction est apportée au stock avec succès","success")
        return redirect(url_for('inventaire.index_correct'))

    if request.method=='GET':
        abort(404)
    return render_template('inventaire/inventaire_produit.html', title=title)

@inventaire.route('/correction')
@login_required
@autorisation_vendeur
def index_correct():
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"
    #Les informations de annuelle
    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])
    voir_operation=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.boutique_id==current_user.boutique_id, Stock.correction==True ).order_by(Stock.id.asc()).all()
    form=CorrectionForm()
    return render_template('inventaire/index_correction.html',title=title, form=form, option_encours=option_encours, listes=voir_operation)



@inventaire.route('/impression/correction')
@login_required
@autorisation_vendeur
def impr_correct():
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"
    #Les informations de annuelle
    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])
    voir_operation=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.boutique_id==current_user.boutique_id, Stock.correction==True ).order_by(Stock.id.asc()).all()
    form=CorrectionForm()
    return render_template('inventaire/imprimercorre.html',title=title, form=form, option_encours=option_encours, listes=voir_operation)

#------------------------------------------- INVENTAIRE DE LA MAGASIN ------------------------------------

@inventaire.route('/magasin/options')
@login_required
@autorisation_maganisier
def conf_index_magasin():

    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"

    stock_graphe=Stock.query.filter(Stock.depot_id==current_user.depot_id,Stock.produit_id!=None,  Stock.solde==True).all()
    produit_dispo=[] #
    serie_produit=[] #Tableau valeur vendue

    for stock_pro in stock_graphe:
      i=stock_pro.disponible
      b=stock_pro.stock_produit.nom_produit
      serie_produit.insert(0,i)
      produit_dispo.insert(0,b)
                

    return render_template('inventaire/conf_inve_ma.html',title=title, option_encours=option_encours, label=produit_dispo, series=serie_produit)



@inventaire.route('/magasin')
@login_required
@autorisation_maganisier
def index_magasin():
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    option_encours="inventaire"
    produit_non_perrisable=[] #Les id des opértaions
    produit_perrisable_encours=[]
    donnees_produits=[] # Les données de tous les produits
    produits_anterieur=[]
    les_produits_inventaire=Produit.query.all()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])

    # Date de l'inventaire
    date_an="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if les_produits_inventaire != []:
        for prod_encours in les_produits_inventaire:
            if prod_encours.perissable==True:
                b=prod_encours.id
                produit_perrisable_encours.insert(0,b)
            else:
                b=prod_encours.id
                produit_non_perrisable.insert(0,b)
        #LES PRODUITS PERRISSABLES
        if len(produit_perrisable_encours) > 1:
            for n in range(len(produit_perrisable_encours)):
                pro_per_sel=produit_perrisable_encours[n]
                #Selection produit encours
                inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produit_id==pro_per_sel, Stock.solde==True).first()
                
                #Les elements du produits
                if inv_prod_solde is not None:
                    nom_produit_inventaire=inv_prod_solde.stock_produit.nom_produit
                    id_produit_inventaire=inv_prod_solde.stock_produit.id
                    image_produit_inventaire=inv_prod_solde.stock_produit.avatar
                    emballage_produit_inventaire=inv_prod_solde.stock_produit.emballage
                    contenue_produit_inventaire=inv_prod_solde.stock_produit.nombre_contenu
                    #Stock disponible totale
                    disponible_totale=inv_prod_solde.disponible
                    inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.depot_id==current_user.depot_id, Stock.produit_id==pro_per_sel, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
                    
                    # Les produits antérieurs
                    for prod_ant_par_produi in inv_produit_anterieur:
                        i=prod_ant_par_produi.id
                        produits_anterieur.insert(0,i)       
                    #Vérification si les deux produit recement stock sont là
                    if len(produits_anterieur) > 1 :
                        stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                        prix=stc.prix_unit
                        stock_mouvement=stc.quantite
                        #Difference du stock
                        diff_stock_mouvement=disponible_totale - stock_mouvement
                        
                        #difference du stock apres le dernier approvissionnement
                        if diff_stock_mouvement >=  1:
                            
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                            stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                            sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
  
                        else:
                            stoc_valeur_enregistre=float(disponible_totale) * float(prix) #la premiere nouvelle valeur
                            sommes_valeur= stoc_valeur_enregistre
                            prix_valeur=float(prix) 
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                            donnees_produits.insert(0,insertion_des_donnees)
                        
                    elif len(produits_anterieur) == 1:
                        
                        stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                        prix=stc.prix_unit
                        stock_mouvement=stc.quantite
                        #Difference du stock
                        diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                        if diff_stock_mouvement >=  1:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                            sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                            prix_valeur=sommes_valeur/disponible_totale
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                        else:
                            stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                            sommes_valeur= disponible_totale * float(prix)
                            prix_valeur=float(prix)
                            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                            donnees_produits.insert(0,insertion_des_donnees)
                    else:

                        stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/inv_prod_solde.disponible
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1,emballage_produit_inventaire, contenue_produit_inventaire ]
                        donnees_produits.insert(0,insertion_des_donnees)
        elif len(produit_perrisable_encours) == 1:

            pro_per_sel=produit_perrisable_encours[0]
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produit_id==pro_per_sel, Stock.solde==True).first()
            #Les elements du produits
            if inv_prod_solde is not None:
                nom_produit_inventaire=inv_prod_solde.stock_produit.nom_produit
                id_produit_inventaire=inv_prod_solde.stock_produit.id
                image_produit_inventaire=inv_prod_solde.stock_produit.avatar
                emballage_produit_inventaire=inv_prod_solde.stock_produit.emballage
                contenue_produit_inventaire=inv_prod_solde.stock_produit.nombre_contenu
                #Stock disponible totale
                disponible_totale=inv_prod_solde.disponible
                inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produit_id==pro_per_sel, Stock.produitboutique_id==None, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
                # Les produits antérieurs
                for prod_ant_par_produi in inv_produit_anterieur:
                    i=prod_ant_par_produi.id
                    produits_anterieur.insert(0,i)
                #Vérification si les deux produit recement stock sont là
                if len(produits_anterieur) > 1 :
                    stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                    prix=stc.prix_unit
                    stock_mouvement=stc.quantite
                    #Difference du stock
                    diff_stock_mouvement=disponible_totale - stock_mouvement
                        #difference du stock apres le dernier approvissionnement
                    if diff_stock_mouvement >=  1:
                            
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                        stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                        sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                    else:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                elif len(produits_anterieur) == 1:

                    stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                    prix=stc.prix_unit
                    stock_mouvement=stc.quantite
                    #Difference du stock
                    diff_stock_mouvement=disponible_totale - stock_mouvement
                    #difference du stock apres le dernier approvissionnement
                    if diff_stock_mouvement >=  1:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                        sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                    else:
                        stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                        sommes_valeur= stoc_valeur_enregistre
                        prix_valeur=sommes_valeur/disponible_totale
                        insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                        donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/inv_prod_solde.disponible
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
        #LES PRODUITS NON PERSSISABLE

        if len(produit_non_perrisable) > 1:
            for n in range(len(produit_non_perrisable)):
                pro_per_sel=produit_non_perrisable[n]
                #Selection produit encours
                inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produit_id==pro_per_sel, Stock.solde==True).first()
                #Les elements du produits
                if inv_prod_solde is not None:
                    nom_produit_inventaire=inv_prod_solde.stock_produit.nom_produit
                    id_produit_inventaire=inv_prod_solde.stock_produit.id
                    image_produit_inventaire=inv_prod_solde.stock_produit.avatar
                    emballage_produit_inventaire=inv_prod_solde.stock_produit.emballage
                    contenue_produit_inventaire=inv_prod_solde.stock_produit.nombre_contenu
                    #Stock disponible totale
                    disponible_totale=inv_prod_solde.disponible
                    sommes_valeur=float(inv_prod_solde.valeur_dispo)
                    prix_valeur= float(sommes_valeur) / float(disponible_totale)
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
        elif len(produit_non_perrisable) == 1:
            pro_per_sel=produit_non_perrisable[0]
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produit_id==pro_per_sel, Stock.solde==True).first()
            #Les elements du produits
            if inv_prod_solde is not None:
                nom_produit_inventaire=inv_prod_solde.stock_produit.nom_produit
                id_produit_inventaire=inv_prod_solde.stock_produit.id
                image_produit_inventaire=inv_prod_solde.stock_produit.avatar
                emballage_produit_inventaire=inv_prod_solde.stock_produit.emballage
                contenue_produit_inventaire=inv_prod_solde.stock_produit.nombre_contenu
                #Stock disponible totale
                disponible_totale=inv_prod_solde.disponible
                sommes_valeur=float(inv_prod_solde.valeur_dispo)
                prix_valeur= float(sommes_valeur) / float(disponible_totale)
                insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
                donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass

    sommes_totale_evaluation=[]
    
    #Valeur totale de la marchandise
    for i in donnees_produits:
        b=i[5]
        sommes_totale_evaluation.insert(0,b)
    retour_somme=sum(sommes_totale_evaluation)
    
    return render_template('inventaire/index_in.html',date_in=date_an, title=title, option_encours=option_encours, inventaire=donnees_produits, valeur=retour_somme)

@inventaire.route('/magasin/produit/<int:id>')
@login_required
@autorisation_maganisier
def inventaire_produit_ma(id):
    #Le clients
    title=f"Inventaire | {current_user.user_entreprise.denomination}"
    produit_non_perrisable=None #Les id des opértaions
    produit_perrisable_encours=None
    donnees_produits=[] # Les données de tous les produits
    produits_anterieur=[]
    les_produits_inventaire=Produit.query.filter_by(id=id).first_or_404()

    aujourd=date.today()
    date_format_avant=str(aujourd).split("-")
    date_annee="%{}%".format(date_format_avant[0])

    # Date de l'inventaire
    date_an="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])

    if les_produits_inventaire is not None:

        if les_produits_inventaire.perissable==True:
            produit_perrisable_encours=les_produits_inventaire.id
        else:
            produit_non_perrisable=les_produits_inventaire.id
                 
        if produit_perrisable_encours is not None:
            pro_per_sel=produit_perrisable_encours
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produit_id==pro_per_sel, Stock.solde==True).first_or_404()
            #Les elements du produits
            nom_produit_inventaire=inv_prod_solde.stock_produit.nom_produit
            id_produit_inventaire=inv_prod_solde.stock_produit.id
            image_produit_inventaire=inv_prod_solde.stock_produit.avatar
            emballage_produit_inventaire=inv_prod_solde.stock_produit.emballage
            contenue_produit_inventaire=inv_prod_solde.stock_produit.nombre_contenu
            #Stock disponible totale
            disponible_totale=inv_prod_solde.disponible
            inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produit_id==pro_per_sel, Stock.produitboutique_id==None, Stock.solde==False, Stock.stockage==True).order_by(Stock.id.desc()).limit(2)
            
            # Les produits antérieurs
            for prod_ant_par_produi in inv_produit_anterieur:
                i=prod_ant_par_produi.id
                produits_anterieur.insert(0,i)
            #Vérification si les deux produit recement stock sont là
            if len(produits_anterieur) > 1 :
                print('ici________________b________')
                stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                prix=stc.prix_unit
                stock_mouvement=stc.quantite
                #Difference du stock
                diff_stock_mouvement=disponible_totale - stock_mouvement
                    #difference du stock apres le dernier approvissionnement
                if diff_stock_mouvement >=  1:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    stc_deux=Stock.query.filter_by(id=produits_anterieur[1]).first()
                    stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(stc_deux.prix_unit) # La deuxieme nouvelle valeur
                    sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    sommes_valeur= stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)

            elif len(produits_anterieur) == 1:
                print('ici________________________')
                stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                prix=stc.prix_unit
                stock_mouvement=stc.quantite
                #Difference du stock
                diff_stock_mouvement=disponible_totale - stock_mouvement
                #difference du stock apres le dernier approvissionnement
                if diff_stock_mouvement >=  1:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    stoc_valeur_enre_deux= float(diff_stock_mouvement) * float(inv_prod_solde.prix_unit) # La deuxieme nouvelle valeur
                    sommes_valeur= stoc_valeur_enre_deux + stoc_valeur_enregistre
                    prix_valeur=sommes_valeur/disponible_totale
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
                else:
                    stoc_valeur_enregistre=float(stock_mouvement) * float(prix) #la premiere nouvelle valeur
                    sommes_valeur= disponible_totale * float(prix)
                    prix_valeur=float(prix)
                    insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                    donnees_produits.insert(0,insertion_des_donnees)
            else:
                print('ici________________________ là')
                stoc_valeur_enregistre=float(inv_prod_solde.valeur_dispo) #la premiere nouvelle valeur
                sommes_valeur= stoc_valeur_enregistre
                prix_valeur=sommes_valeur/inv_prod_solde.disponible
                insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,1, emballage_produit_inventaire, contenue_produit_inventaire]
                donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
        #LES PRODUITS NON PERSSISABLE
        if produit_non_perrisable is not None:
            pro_per_sel=produit_non_perrisable
            #Selection produit encours
            inv_prod_solde=Stock.query.filter(Stock.datest.ilike(date_annee), Stock.produit_id==pro_per_sel, Stock.solde==True).first_or_404()
            #Les elements du produits
            nom_produit_inventaire=inv_prod_solde.stock_produit.nom_produit
            id_produit_inventaire=inv_prod_solde.stock_produit.id
            image_produit_inventaire=inv_prod_solde.stock_produit.avatar
            emballage_produit_inventaire=inv_prod_solde.stock_produit.emballage
            contenue_produit_inventaire=inv_prod_solde.stock_produit.nombre_contenu
            #Stock disponible totale
            inv_produit_anterieur=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produit_id==pro_per_sel, Stock.solde==False,Stock.produitboutique_id==None, Stock.stockage==True).order_by(Stock.id.desc()).first()
            disponible_totale=inv_prod_solde.disponible
            
            sommes_valeur=float(inv_prod_solde.disponible) * float(inv_produit_anterieur.prix_unit)
            prix_valeur= float(inv_produit_anterieur.prix_unit)
            insertion_des_donnees=[id_produit_inventaire, image_produit_inventaire,nom_produit_inventaire, disponible_totale,prix_valeur,sommes_valeur,0, emballage_produit_inventaire, contenue_produit_inventaire]
            donnees_produits.insert(0,insertion_des_donnees)
        else:
            pass
    #Liste des opérations de l'inventaire
    voir_operation=Stock.query.filter(Stock.datest.ilike(date_annee),Stock.produit_id==id, Stock.depot_id==current_user.depot_id).order_by(Stock.id.asc()).all()
          
    sommes_totale_evaluation=[]
    #Valeur totale de la marchandise
    for i in donnees_produits:
        b=i[5]
        sommes_totale_evaluation.insert(0,b)
    retour_somme=sum(sommes_totale_evaluation)

    

    return render_template('inventaire/inventaire_produit_ma.html',produits=les_produits_inventaire, date_in=date_an, listes=voir_operation, title=title, inventaire=donnees_produits, valeur=retour_somme)
