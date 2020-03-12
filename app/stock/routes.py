from flask import render_template, flash, url_for, redirect, request, session, g
from .. import db, bcrypt
from ..models import User, Boutique, Depot, Stock
from app.stock.forms import StockageForm
from app.stock.utility import save_picture, verification_de_role
from flask_login import login_user, current_user, login_required


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
      stock_disponible=Stock.query.filter_by(produit_id=produit_id.id, depot_id=current_user.user_depot.id).order_by(Stock.id.desc()).first()
      if stock_disponible is None:
         qte_disponible=quantite #Quantité disponible pour le premier stockage du produit dans le dépot
         valeur_disponible=prix_achat*quantite #Ainsi que sa valeur
      else:
         qte_disponible=stock_disponible.disponible + quantite
         valeur_disponible_act_op=prix_achat*quantite
         valeur_disponible= valeur_disponible_act_op + stock_disponible.valeur_dispo

      #Enregistrement des quantité de stockage de produit
      stockage=Stock(quantite=quantite, valeur=val_op, date=date_operation, prix_unit=prix_achat, disponible=qte_disponible, valeur_dispo=valeur_disponible,
                     stockage=True, produit_id=produit_id.id, depot_id=current_user.user_depot.id, stock_user=current_user, fournisseur_id=form.fournissseur_stock.data.id)
      db.session.add(stockage)
      db.session.commit()
      terminer_bouton=True
      flash("Vous avez stocké {} {} du produit ({}) dans le dépôt {} avec succès".format(quantite,produit_id.emballage, produit_id.nom_produit, current_user.user_depot.nom_depot),'success')
      return redirect(url_for('stock.stockagedepot'))
      
   return render_template('stock/stockage.html', title=title, form=form, terminer_bouton=terminer_bouton)
