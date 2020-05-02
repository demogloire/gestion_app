from flask import render_template, flash, url_for, redirect, request, session, g
from .. import db, bcrypt
from datetime import date, datetime
from ..models import User, Boutique, Depot, Stock, Produit, Produitboutique
from app.stock.forms import StockageForm, StockageErreurForm, BoutiqueRechForm, AnneeTransForm, MensuelTransForm
from app.stock.utility import save_picture, verification_de_role, autorisation_magasinier
from flask_login import login_user, current_user, login_required
from sqlalchemy import func


from . import stock

""" Ajout utilisateur"""
@stock.route('/stockage_depot', methods=['GET','POST'])
@login_required
@autorisation_magasinier
def stockagedepot():
   title="Stock dépôt"
   #Formulaire
   form=StockageForm()
   #Activ stock
   option_encours="stock"
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
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée

      prix_achat=None #Le prix d'achat de la marchandise
      #Affectation du prix d'achat du produit
      if prix_d==0:
         prix_achat=produit_id.cout_d_achat
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
         valeur_disponible=float(prix_achat*quantite) #Ainsi que sa valeur
      else:
         qte_disponible=stock_disponible.disponible + quantite
         valeur_disponible_act_op=float(prix_achat*quantite)
         valeur_disponible=valeur_disponible_act_op + float(stock_disponible.valeur_dispo)
         stock_disponible.solde=False
         db.session.commit()

      #Enregistrement des quantité de stockage de produit
      stockage=Stock(quantite=quantite, valeur=val_op, datest=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
                     stockage=True, produit_id=produit_id.id, depot_id=current_user.user_depot.id, stock_user=current_user, fournisseur_id=form.fournissseur_stock.data.id, solde=solde_active)
      db.session.add(stockage)
      db.session.commit()
      #Détermination de l'emballage
      emballage=produit_id.emballage
      if produit_id.emballage !="Carton" or produit_id.emballage !="Box" :
         emballage="Pièce"
      #Gestion de la quantité de l'opération
      if quantite > 1:
         flash("Vous avez stocké {} {}s du produit ({}) dans le dépôt {} avec succès".format(quantite,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
      else:
         flash("Vous avez stocké {} {} du produit ({}) dans le dépôt {} avec succès".format(quantite,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
      
      return redirect(url_for('stock.stockagedepot'))
      
   return render_template('stock/stockage.html',option_encours=option_encours, title=title, form=form, terminer_bouton=terminer_bouton)



""" Erreur de stockage de marchandise"""
@stock.route('/erreur_stockage_depot', methods=['GET','POST'])
@login_required
@autorisation_magasinier
def erreurstockagedepot():
   title="Erreur de stockage dépôt"
   #Formulaire
   form=StockageErreurForm()
   #Activ stock
   option_encours="stock"
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
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée

      prix_achat=None #Le prix d'achat de la marchandise
      #Affectation du prix d'achat du produit
      if prix_d==0:
         prix_achat=produit_id.cout_d_achat
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
            valeur_disponible= float(stock_disponible.valeur_dispo) - val_op # Valeur de la quantité de soustraction dans le stock
            #Change de Solde
            stock_disponible.solde=False
            db.session.commit()

            #Enregistrement des quantité de stockage de produit
            stockage=Stock(quantite=quantite, valeur=val_op, datest=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
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
            
            return redirect(url_for('stock.index'))
         else:
            emballage=produit_id.emballage
            if produit_id.emballage !="Carton":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if stock_disponible.disponible >= 1:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de ${}".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, round(stock_disponible.valeur_dispo,2) ),'danger')
            else:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de ${}".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, round(stock_disponible.valeur_dispo,2)),'danger')
      else:
         flash("Désolé ce produit ne pas dans votre dépôt",'danger')
            
   return render_template('stock/erreur.html',option_encours=option_encours, title=title, form=form)



""" Transfert de la marchandise"""
@stock.route('/transfert_boutique', methods=['GET','POST'])
@login_required
@autorisation_magasinier
def transfertboutique():
   title="Transfer boutique"
   #Formulaire
   form=BoutiqueRechForm()
   #Activ stock
   option_encours="stock"
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
      date_no_formater=str(form.date_op.data)
      date_format_avant=date_no_formater.split("/")
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée

      

      prix_achat=None #Le prix d'achat de la marchandise
      #Affectation du prix d'achat du produit
      if prix_d==0:
         prix_achat=produit_id.cout_d_achat
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
                           description=produit_id.description,vt_gros_piece=produit_id.vt_gros_piece,vt_detaille_piece=produit_id.vt_detaille_piece,\
                           vt_gros_entier=produit_id.vt_gros_entier,cout_d_achat=produit_id.cout_d_achat, avatar=produit_id.avatar,\
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
         if stock_disponible.disponible >= quantite and stock_disponible.valeur_dispo >= val_op:
            qte_disponible= stock_disponible.disponible - quantite #Quantité de soustraction dans le stock
            valeur_disponible= float(stock_disponible.valeur_dispo) - val_op # Valeur de la quantité de soustraction dans le stock
            #Change de Solde
            stock_disponible.solde=False
            db.session.commit()
            #Transfert de la quantité
            stockage=Stock(quantite=quantite, valeur=val_op, datest=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
                           transfert=True, solde=stock_disponible_solde, produit_id=produit_id.id, depot_id=current_user.user_depot.id, stock_user=current_user,boutique_id=boutique_id )
            db.session.add(stockage)
            db.session.commit()
            #Reception de la quantité
            qte_disponible_boutique=None
            valeur_disponible_boutique=None
            #Nouvelle données sur la quantité et le prix
            qte_nouvelle_boutique=None
            prix_nouvelle_boutique=None

            if produit_id.emballage == "Carton" or produit_id.emballage == "Box":
                  nbre_conte_element=None
                  if produit_id.nombre_contenu==0:
                     nbre_conte_element=1
                  else:
                     nbre_conte_element=produit_id.nombre_contenu

                  qte_nouvelle_boutique=(quantite*nbre_conte_element)
                  prix_nouvelle_boutique=float(val_op/qte_nouvelle_boutique)
                  
            elif produit_id.emballage == "Vrac" or produit_id.emballage == "Sac" :
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
               valeur_disponible_boutique=float(stock_disponible_boutique.valeur_dispo) + val_con
               #Mise à jour de la quantité d
               stock_disponible_boutique.solde=False
               db.session.commit()
            #Recuperation des informations sur le produit apres enregistrements
            #Change de Solde
            stockage_boutique=Stock(quantite=qte_nouvelle_boutique, valeur=val_con, datest=date_operation, prix_unit=prix_nouvelle_boutique, 
                           disponible=qte_disponible_boutique, 
                           valeur_dispo=valeur_disponible_boutique, stockage=True, produit_id=produit_id.id, boutique_id=boutique_id, 
                           stock_user=current_user, produitboutique_id=id_produit_boutique, solde=solde_boutique)
            db.session.add(stockage_boutique)
            db.session.commit()
            #Détermination de l'emballage
            emballage=produit_id.emballage
            if produit_id.emballage =="Sac" and produit_id.emballage =="Vrac":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if quantite > 1:
               flash("Vous avez envoyé {} {}s du produit ({}) dans la boutique {} avec succès".format(quantite,emballage, produit_id.nom_produit, form.boutiques_cherch.data.nom_boutique),'success')
            else:
               flash("Vous avez envoyé  {} {} du produit ({}) dans la boutique {} avec succès".format(quantite,emballage, produit_id.nom_produit, form.boutiques_cherch.data.nom_boutique),'success')
            
            return redirect(url_for('stock.transfertboutique'))
         else:
            emballage=produit_id.emballage
            if produit_id.emballage !="Carton":
               emballage="Pièce"
            #Gestion de la quantité de l'opération
            if stock_disponible.disponible >=1:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de ${}".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, round(stock_disponible.valeur_dispo,2)  ),'danger')
            else:
               flash("Vous avez une quantité de {} {}s du produit ({}) dans le dépôt {} avec une valeur de ${}".format(stock_disponible.disponible,emballage, produit_id.nom_produit, current_user.user_depot.nom_depot, round(stock_disponible.valeur_dispo,2)),'danger')
      else:
         flash("Désolé ce produit ne pas dans votre dépôt",'danger')
            
   return render_template('stock/transfer.html',option_encours=option_encours, title=title, form=form)


#Liste de sockage du dépôt
@stock.route('/')
@login_required
@autorisation_magasinier
def index():
    #Le stock
    title="Gestion Lambda"
    #Activ stock
    option_encours="stock"
    
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
           
    return render_template('stock/index.html',option_encours=option_encours, title=title, listes=list_stock, label=produit_dispo, series=serie_produit)

#Liste les transfert du dépôt
@stock.route('/transfert')
@login_required
@autorisation_magasinier
def transfert_depot():
    #Le stock
    title="Gestion Lambda"
    #Activ stock
    option_encours="stock"
    #Stock disponible
    page= request.args.get('page', 1, type=int)
    list_stock=Stock.query.filter_by(depot_id=current_user.user_depot.id, transfert=True).order_by(Stock.id.desc()).paginate(page=page, per_page=50)

    return render_template('stock/transfert.html', option_encours=option_encours, title=title, listes=list_stock)

#Liste les transfert du dépôt
@stock.route('/triertransfert', methods=['GET','POST'])
@login_required
@autorisation_magasinier
def trier_depot():
    #Le stock
    title="Gestion Lambda"
    #variable de vérification
    #Activ stock
    option_encours="stock"
    #Stock disponible
    
    list_stock=None #Liste journalière
    list_stock_mois=None #Liste mensuelle
    stock_annee=None #Liste annuelle

    page= request.args.get('page', 1, type=int)
    #Liste de stock
    #list_stock=Stock.query.filter(Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).paginate(page=page, per_page=50)
    ver="No"  
    
    #Formulaire de recherche
    form=AnneeTransForm()
    
   
    #Verification par l'année
    if form.validate_on_submit():
       
       date_format_avant=form.date_annee_recherche.data.split("/")
       
       date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée journalièment
       date_operation_mois="{}-{}".format(date_format_avant[2],date_format_avant[1]) #La date formatée mensuellement
       date_operation_annuelle="{}".format(date_format_avant[2]) #La date formatée annuellement

       mois='%{}%'.format(date_operation_mois)
       annne_stock='%{}%'.format(date_operation_annuelle)

       produit=form.produit_stock.data
       boutique=form.boutiques_cherch.data
      #Vérification si le produit et la boutique ne pas passé
       if produit == 0:
          if boutique==0:
             list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
               ver="Novide"
       #Vérification si la boutique et le produit ne pas passé
       if boutique==0:
          if produit==0:
             list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             stock=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             if list_stock is not None or list_stock_mois is not None or stock is not None :
               ver="Novide"
      #Vérification si le produit est  passe et la boutique est  passé
       if produit !=0 :
          if boutique !=0 :
             list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.boutique_id==boutique.id,Stock.transfert==True).order_by(Stock.id.desc()).all()
             list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.boutique_id==boutique.id,Stock.transfert==True).order_by(Stock.id.desc()).all()
             stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.boutique_id==boutique.id,Stock.transfert==True).order_by(Stock.id.desc()).all()
             if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
               ver="Novide"
            #Vérification si la boutique ne pas passé
          if boutique ==0 :
             list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
               ver="Novide"
       #Vérification si la boutique est  passe et le produit  est  passé
       if boutique  !=0 :
          if produit !=0 :
             list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.boutique_id==boutique.id,Stock.transfert==True).order_by(Stock.id.desc()).all()
             list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.boutique_id==boutique.id,Stock.transfert==True).order_by(Stock.id.desc()).all()
             stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id, Stock.boutique_id==boutique.id,Stock.transfert==True).order_by(Stock.id.desc()).all()
             if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
               ver="Novide"
            #Vérification si le produit ne pas passé
          if produit ==0 :
             list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id,Stock.boutique_id==boutique.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id,Stock.boutique_id==boutique.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id,Stock.boutique_id==boutique.id, Stock.transfert==True).order_by(Stock.id.desc()).all()
             if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
               ver="Novide"
       
    return render_template('stock/trier.html',option_encours=option_encours, title=title, listes=list_stock, form=form, ver=ver, list_stock_mois=list_stock_mois, list_stock_annee=stock_annee)


#Recherche du stock d'une date
@stock.route('/stockdate', methods=['GET','POST'])
@login_required
def stock_de_depot():
    #Le stock
    title="Gestion Lambda"
    #variable de vérification
    #Activ stock
    option_encours="stock"
    #Stock disponible
    list_stock=None #Liste journalière
    list_stock_mois=None #Liste mensuelle
    stock_annee=None #Liste annuelle

    page= request.args.get('page', 1, type=int)
    #Liste de stock
    #list_stock=Stock.query.filter(Stock.depot_id==current_user.user_depot.id, Stock.transfert==True).order_by(Stock.id.desc()).paginate(page=page, per_page=50)
    ver="No"  
    
    #Formulaire de recherche
    form=MensuelTransForm()


    #Verification par l'année
    if form.validate_on_submit():
       

       date_format_avant=form.date_annee_recherche.data.split("/")
       
       date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée journalièment
       date_operation_mois="{}-{}".format(date_format_avant[2],date_format_avant[1]) #La date formatée mensuellement
       date_operation_annuelle="{}".format(date_format_avant[2]) #La date formatée annuellement

       mois='%{}%'.format(date_operation_mois)
       annne_stock='%{}%'.format(date_operation_annuelle)

       produit=form.produit_stock.data

      #Vérification si le produit et la boutique ne pas passé
       if produit == 0:
          list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id).order_by(Stock.id.desc()).all()
          list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id).order_by(Stock.id.desc()).all()
          stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id).order_by(Stock.id.desc()).all()
          if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
            ver="Novide"

      #Vérification si le produit est  passe et la boutique est  passé
       if produit !=0 :
          list_stock=Stock.query.filter(Stock.datest==date_operation,Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id).order_by(Stock.id.desc()).all()
          list_stock_mois=Stock.query.filter(Stock.datest.ilike(mois),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id).order_by(Stock.id.desc()).all()
          stock_annee=Stock.query.filter(Stock.datest.ilike(annne_stock),Stock.depot_id==current_user.user_depot.id,Stock.produit_id==produit.id).order_by(Stock.id.desc()).all()
          if list_stock is not None or list_stock_mois is not None or stock_annee is not None :
            ver="Novide"
       
    return render_template('stock/cherche.html',option_encours=option_encours, title=title, listes=list_stock, form=form, ver=ver, list_stock_mois=list_stock_mois, list_stock_annee=stock_annee)


#--------------------------------------------------- GESTION DE STOCK VENDEUR ---------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------


#Liste de sockage du dépôt
@stock.route('/boutique/disponible')
@login_required
def boutique_stock():
    #Le stock
    title="Stock disponible | {} ".format(current_user.user_entreprise.denomination)
    #Activ stock
    option_encours="stock"
    
    #Stock disponible
    page= request.args.get('page', 1, type=int)
    list_stock=Stock.query.filter(Stock.boutique_id==current_user.boutique_id, Stock.produitboutique_id!=None, Stock.solde==True).order_by(Stock.id.desc()).paginate(page=page, per_page=50)

    stock_graphe=Stock.query.filter(Stock.boutique_id==current_user.boutique_id,Stock.produitboutique_id!=None,  Stock.solde==True).all()
    produit_dispo=[] #
    serie_produit=[] #Tableau valeur vendue

    for stock_pro in stock_graphe:
      i=stock_pro.disponible
      b=stock_pro.stock_produitboutique.nom_produit
      serie_produit.insert(0,i)
      produit_dispo.insert(0,b)

    return render_template('stock/boutique_index.html',option_encours=option_encours, title=title, listes=list_stock, label=produit_dispo, series=serie_produit)



       
       

