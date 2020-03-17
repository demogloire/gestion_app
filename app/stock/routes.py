from flask import render_template, flash, url_for, redirect, request, session, g
from .. import db, bcrypt
from ..models import User, Boutique, Depot, Stock, Produit, Produitboutique
from app.stock.forms import StockageForm, StockageErreurForm, BoutiqueRechForm
from app.stock.utility import save_picture, verification_de_role
from flask_login import login_user, current_user, login_required
from sqlalchemy import func


from . import stock

""" Ajout utilisateur"""
@stock.route('/stockage_depot', methods=['GET','POST'])
@login_required
def stockagedepot():
   title="Stock dépôt"
   #Formulaire
   form=StockageForm()

   #Verification de l'authentification
   if current_user.role !="Magasinier":
      return redirect(url_for('main.index'))

   #Bouton terminer
   terminer_bouton=None

   #Enregistrement de l'opération
   if form.validate_on_submit():
      produit_id=form.produit_stock.data #Les informations de produit
      quantite=form.quantite.data #La quantité de produit
      prix_d=form.prix_d.data
      fournisseur_id=form.fournissseur_stock.data.id # Le fournisseur

      #formatage de la date 
      date_no_formater=form.date_op.data
      date_format_avant=date_no_formater.split("/")
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[0],date_format_avant[1]) #La date formatée

      prix_achat=None #Le prix d'achat de la marchandise
      #Affectation du prix d'achat du produit
      if prix_d==0:
         prix_achat=produit_id.prix_achat_g
      else:
         prix_achat=prix_d
      
      #Valeur de l'operation
      val_op=prix_achat*quantite
      
      #Verification de la dernière stock
      qte_disponible=None
      valeur_disponible=None
      solde_active=True
      stock_disponible=Stock.query.filter_by(produit_id=produit_id.id, depot_id=current_user.user_depot.id).order_by(Stock.id.desc()).first()
      if stock_disponible is None:
         qte_disponible=quantite #Quantité disponible pour le premier stockage du produit dans le dépot
         valeur_disponible=prix_achat*quantite #Ainsi que sa valeur
      else:
         qte_disponible=stock_disponible.disponible + quantite
         valeur_disponible_act_op=float(prix_achat*quantite)
         valeur_disponible=float(valeur_disponible_act_op + stock_disponible.valeur_dispo)
         stock_disponible.solde=False
         db.session.commit()

      #Enregistrement des quantité de stockage de produit
      stockage=Stock(quantite=quantite, valeur=val_op, date=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
                     stockage=True, produit_id=produit_id.id, depot_id=current_user.user_depot.id, stock_user=current_user, fournisseur_id=form.fournissseur_stock.data.id, solde=solde_active)
      db.session.add(stockage)
      db.session.commit()
      #Détermination de l'emballage
      emballage=produit_id.emballage
      if produit_id.emballage !="Carton":
         emballage="Pièce"
      #Gestion de la quantité de l'opération
      if quantite > 1:
         flash("Vous avez stocké {} {}s du produit ({}) dans le dépôt {} avec succès".format(quantite,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
      else:
         flash("Vous avez stocké {} {} du produit ({}) dans le dépôt {} avec succès".format(quantite,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
      
      return redirect(url_for('stock.stockagedepot'))
      
   return render_template('stock/stockage.html', title=title, form=form, terminer_bouton=terminer_bouton)



""" Erreur de stockage de marchandise"""
@stock.route('/erreur_stockage_depot', methods=['GET','POST'])
@login_required
def erreurstockagedepot():
   title="Erreur de stockage dépôt"
   #Formulaire
   form=StockageErreurForm()

   #Verification de l'authentification
   if current_user.role !="Magasinier":
      return redirect(url_for('main.index'))

 
   #Enregistrement de l'opération
   if form.validate_on_submit():
      produit_id=form.produit_stock.data #Les informations de produit
      quantite=form.quantite.data #La quantité de produit
      prix_d=form.prix_d.data

      #formatage de la date 
      date_no_formater=form.date_op.data
      date_format_avant=date_no_formater.split("/")
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[0],date_format_avant[1]) #La date formatée

      prix_achat=None #Le prix d'achat de la marchandise
      #Affectation du prix d'achat du produit
      if prix_d==0:
         prix_achat=produit_id.prix_achat_g
      else:
         prix_achat=prix_d
      
      #Valeur de l'operation
      val_op= float(prix_achat*quantite)
      
      #Verification de la dernière stock
      qte_disponible=None
      valeur_disponible=None
      stock_disponible=Stock.query.filter_by(produit_id=produit_id.id, depot_id=current_user.user_depot.id).order_by(Stock.id.desc()).first()
      solde_disponible=True #Mise à jour du stock disponbible
      if stock_disponible is not None:
         if stock_disponible.disponible > quantite and stock_disponible.valeur_dispo > val_op:
            qte_disponible= stock_disponible.disponible - quantite #Quantité de soustraction dans le stock
            valeur_disponible= stock_disponible.valeur_dispo - val_op # Valeur de la quantité de soustraction dans le stock
            #Change de Solde
            stock_disponible.solde=False
            db.session.commit()

            #Enregistrement des quantité de stockage de produit
            stockage=Stock(quantite=quantite, valeur=val_op, date=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
                           erreur=True, produit_id=produit_id.id, depot_id=current_user.user_depot.id, stock_user=current_user, solde=solde_disponible)
            db.session.add(stockage)
            db.session.commit()
            #Détermination de l'emballage
            emballage=produit_id.emballage
            if produit_id.emballage !="Carton":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if quantite > 1:
               flash("Vous avez retiré {} {}s du produit ({}) dans le dépôt {} avec succès".format(quantite,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
            else:
               flash("Vous avez retiré {} {} du produit ({}) dans le dépôt {} avec succès".format(quantite,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
            
            return redirect(url_for('stock.stockagedepot'))
         else:
            emballage=produit_id.emballage
            if produit_id.emballage !="Carton":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if stock_disponible.disponible > 1:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de {} UM ".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, stock_disponible.valeur_dispo ),'danger')
            else:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de {} UM".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, stock_disponible.valeur_dispo),'danger')
      else:
         flash("Désolé ce produit ne pas dans votre dépôt",'danger')
            
   return render_template('stock/erreur.html', title=title, form=form)



""" Transfert de la marchandise"""
@stock.route('/transfert_boutique', methods=['GET','POST'])
@login_required
def transfertboutique():
   title="Transfer boutique"
   #Formulaire
   form=BoutiqueRechForm()

   #Verification de l'authentification
   if current_user.role !="Magasinier":
      return redirect(url_for('main.index'))

 
   #Enregistrement de l'opération
   if form.validate_on_submit():
      produit_id=form.produit_stock.data #Les informations de produit
      quantite=form.quantite.data #La quantité de produit
      prix_d=form.prix_d.data #Le transfert
      boutique_id=form.boutiques_cherch.data.id #Boutique approvisionner


      #formatage de la date 
      date_no_formater=form.date_op.data
      date_format_avant=date_no_formater.split("/")
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[0],date_format_avant[1]) #La date formatée

      prix_achat=None #Le prix d'achat de la marchandise
      #Affectation du prix d'achat du produit
      if prix_d==0:
         prix_achat=produit_id.prix_achat_g
      else:
         prix_achat=prix_d
      
      #Valeur de l'operation
      val_op= float(prix_achat*quantite)
      
      #Requête de vérfication de l'existene du pro dans le stock de boutique
      produit_bout=Produitboutique.query.filter_by(produit_id=produit_id.id, boutique_id=boutique_id).first()

      #Id du produit
      id_produit_boutique=None

      #Enregistrement du produit
      if produit_bout is None:

         produit_enregistrement=Produitboutique(code_produit=produit_id.code_produit, nom_produit=produit_id.nom_produit,\
                           description=produit_id.description,prix_achat=produit_id.prix_achat,prix_vente=produit_id.prix_vente,\
                           prix_achat_g=produit_id.prix_achat_g,prix_vente_g=produit_id.prix_vente_g, avatar=produit_id.avatar,\
                           emballage=produit_id.emballage, nombre_contenu=produit_id.nombre_contenu,categorie_id=produit_id.categorie_id,\
                           boutique_id=boutique_id, produit_id=produit_id.id)
         db.session.add(produit_enregistrement)
         db.session.commit()

      else:
         id_produit_boutique=produit_bout.id   
      #Verification de la dernière stock
      qte_disponible=None
      valeur_disponible=None
      stock_disponible=Stock.query.filter_by(produit_id=produit_id.id, depot_id=current_user.user_depot.id).order_by(Stock.id.desc()).first()
      stock_disponible_solde=True
      if stock_disponible is not None:
         if stock_disponible.disponible > quantite and stock_disponible.valeur_dispo > val_op:
            qte_disponible= stock_disponible.disponible - quantite #Quantité de soustraction dans le stock
            valeur_disponible= stock_disponible.valeur_dispo - val_op # Valeur de la quantité de soustraction dans le stock
            #Change de Solde
            stock_disponible.solde=False
            db.session.commit()
            #Transfert de la quantité
            stockage=Stock(quantite=quantite, valeur=val_op, date=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
                           transfert=True, solde=stock_disponible_solde, produit_id=produit_id.id, depot_id=current_user.user_depot.id, stock_user=current_user,boutique_id=boutique_id )
            db.session.add(stockage)
            db.session.commit()
            #Reception de la quantité
            qte_disponible_boutique=None
            valeur_disponible_boutique=None
            #Nouvelle données sur la quantité et le prix
            qte_nouvelle_boutique=None
            prix_nouvelle_boutique=None

            if produit_id.emballage != "Vrac" or produit_id.emballage != "Sac": 
               qte_nouvelle_boutique=(quantite*produit_id.nombre_contenu)
               prix_nouvelle_boutique=float(prix_achat/qte_nouvelle_boutique)
            else:
               qte_nouvelle_boutique=quantite
               prix_nouvelle_boutique=prix_achat
            #Valeur de l'operation en conversion
            val_con= float(qte_nouvelle_boutique*prix_nouvelle_boutique)

            produit_boutique=Produitboutique.query.filter_by(produit_id=produit_id.id, boutique_id=boutique_id).first()
            id_produit_boutique=produit_boutique.id

            #La vérification des informations
            stock_disponible_boutique=Stock.query.filter_by(produitboutique_id=id_produit_boutique, boutique_id=boutique_id).order_by(Stock.id.desc()).first()
            solde_boutique=True
            if stock_disponible_boutique is None:
               qte_disponible_boutique=qte_nouvelle_boutique 
               valeur_disponible_boutique=float(prix_nouvelle_boutique*qte_nouvelle_boutique)
            else:
               qte_disponible_boutique=stock_disponible_boutique.quantite + qte_nouvelle_boutique
               valeur_disponible_boutique=float(stock_disponible_boutique.valeur_dispo + val_con)
               #Mise à jour de la quantité d
               stock_disponible_boutique.solde=False
               db.session.commit()
            #Recuperation des informations sur le produit apres enregistrements
            #Change de Solde
            

            stockage_boutique=Stock(quantite=qte_nouvelle_boutique, valeur=val_con, date=date_operation, prix_unit=prix_nouvelle_boutique, 
                           disponible=qte_disponible_boutique, 
                           valeur_dispo=valeur_disponible_boutique, stockage=True, produit_id=produit_id.id, boutique_id=boutique_id, 
                           stock_user=current_user, produitboutique_id=id_produit_boutique, solde=solde_boutique)
            db.session.add(stockage_boutique)
            db.session.commit()


            #Détermination de l'emballage
            emballage=produit_id.emballage
            if produit_id.emballage !="Sac" and produit_id.emballage !="Vrac":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if quantite > 1:
               flash("Vous avez envoyé {} {}s du produit ({}) dans la boutique {} avec succès".format(quantite,emballage, produit_id.nom_produit, form.boutiques_cherch.data.nom_boutique),'success')
            else:
               flash("Vous avez envoyé  {} {} du produit ({}) dans la boutique {} avec succès".format(quantite,emballage, produit_id.nom_produit, form.boutiques_cherch.data.nom_boutique),'success')
            
            return redirect(url_for('stock.stockagedepot'))
         else:
            emballage=produit_id.emballage
            if produit_id.emballage !="Carton":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if stock_disponible.disponible > 1:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de {} UM ".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, stock_disponible.valeur_dispo ),'danger')
            else:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de {} UM".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, stock_disponible.valeur_dispo),'danger')
      else:
         flash("Désolé ce produit ne pas dans votre dépôt",'danger')
            
   return render_template('stock/transfer.html', title=title, form=form)


#Liste de sockage du dépôt
@stock.route('/')
@login_required
def index():
    #Le stock
    title="Gestion Lambda"
    
    #Stock disponible
    page= request.args.get('page', 1, type=int)
    list_stock=Stock.query.filter_by(depot_id=current_user.user_depot.id).order_by(Stock.id.desc()).paginate(page=page, per_page=50)

    stock_graphe=Stock.query.filter(Stock.depot_id==current_user.user_depot.id, Stock.solde==True ).all()
    produit_dispo=[] #
    serie_produit=[] #Tableau valeur vendue

    for stock_pro in stock_graphe:
      i=stock_pro.disponible
      b=stock_pro.stock_produit.code_produit
      serie_produit.insert(0,i)
      produit_dispo.insert(0,b)
           
   

    return render_template('stock/index.html', title=title, listes=list_stock, label=produit_dispo, series=serie_produit)

