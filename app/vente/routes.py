from flask import render_template, flash, url_for, redirect, request, session, g
from .. import db, bcrypt
from ..models import User, Boutique, Depot, Stock, Produit, Produitboutique, Facture, Vente, Payement, Operation, Comptes, Valeurvente
from app.vente.forms import RechercheFiltreAdminProForm, RecherchePlageAdminProduiForm, RecherchePlageAdminForm, FactureForm, RechercheFiltreAdminForm, VenteFactureForm,RechercheFactureRapForm, RechercheForm, FactureAcForm,  PayementFactureForm,  DiminutionFactureForm, RechercheAFactureForm,  VenteFactureGForm, DiminutionGFactureForm, RechercheFactureForm, RechercheDFactureForm
import app.pack_fonction.fonction as utilitaire
from app.vente.autorisation import vente_plage_triage_admin, produit_triage_par_option, produit_triage_mensuel, vente_plage_detaille_boutique,vente_plage_triage, vente_mensuelle_triage, vente_mensuelle_detaille_boutique, autorisation_vendeur, dat_anne, vente_inde, vente_mensuelle, vente_mensuelle_detaille, autorisation_vendeur_gerant, autorisation_gerant
from datetime import datetime, date
from flask_login import login_user, current_user, login_required
from sqlalchemy import func
from decimal import Decimal



from . import vente


# ---------------------- LES INFORMATIONS DE LA FACTURE---------------------------------------------------
""" Ajouter une facture"""
@vente.route('/facturation', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def facturecash():
   option_encours='vente'
   title='Vente'
   #Code de la facture
   codefacture=utilitaire.codefacture()
   #Vérification de l'existence de la facture
   if utilitaire.verification_facture()==False:
      return redirect(url_for('vente.cash'))
   #Utilitaire
   client_unique=utilitaire.client_defautl()
   #Type de la vente
   type_validation_encours=utilitaire.validationtype()
   #Dette.
   dette_ver=utilitaire.validationtype_dette()
   cash_dette_encours=None
   #Controle de facture
   dette_controle_formulaire=None
   if type_validation_encours is None:
      #Controle de la facture de dette
      if dette_ver is None:
         pass
      else:
         if dette_ver==1:
            dette_controle_formulaire=True
         else:
            dette_controle_formulaire=False  
   else:
      if type_validation_encours==1:
         cash_dette_encours=True
      else:
         cash_dette_encours=False
      
   #Formulaire
   form=FactureForm()
   #Enregistrement de la facture
   if form.validate_on_submit():
      client_nv=utilitaire.client_entree(form.client_input.data) #Enregistrement et retour clien
      code_fact_one=utilitaire.verification_facture() #Vérfication code de la facture
      #Formatage de la date
      date_no_formater=str(form.date_op.data)
      date_format_avant=date_no_formater.split("-")
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée
      session["datefacture"]=date_operation
      #Enregistrement selon les information du client
      if client_nv is not None and form.client_input_cherch.data is not None:
         if cash_dette_encours is not None:
            operation_facture=Facture(code_facture=code_fact_one, date=date_operation, cash=True, client_id=client_nv.id, user_id=current_user.id, boutique_id=current_user.boutique_id,type_vente=cash_dette_encours)
            db.session.add(operation_facture)
            db.session.commit()
            session["idfacture"]=operation_facture.id
            #Facturation cash
            if cash_dette_encours==False:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.infofacture'))
            else:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.grosinfofacture'))
         elif dette_controle_formulaire is not None:
            operation_facture=Facture(code_facture=code_fact_one, date=date_operation, dette=True, client_id=client_nv.id, user_id=current_user.id, boutique_id=current_user.boutique_id,type_vente=dette_controle_formulaire)
            db.session.add(operation_facture)
            db.session.commit()
            session["idfacture"]=operation_facture.id
            #Facturation cash
            if dette_controle_formulaire==False:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.infofacture'))
            else:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.grosinfofacture'))

      elif client_nv is None and form.client_input_cherch.data is not None :
         if cash_dette_encours is not None:
            operation_facture=Facture(code_facture=code_fact_one, date=date_operation, cash=True, client_id=form.client_input_cherch.data.id, user_id=current_user.id, boutique_id=current_user.boutique_id, type_vente=cash_dette_encours)
            db.session.add(operation_facture)
            db.session.commit()
            session["idfacture"]=operation_facture.id
            #Facture cash
            if cash_dette_encours==False:
               flash('Etablir la facture','success')
               return redirect(url_for('vente.infofacture'))
            else:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.grosinfofacture'))
         elif dette_controle_formulaire is not None:
            operation_facture=Facture(code_facture=code_fact_one, date=date_operation, dette=True, client_id=form.client_input_cherch.data.id, user_id=current_user.id, boutique_id=current_user.boutique_id, type_vente=dette_controle_formulaire)
            db.session.add(operation_facture)
            db.session.commit()
            session["idfacture"]=operation_facture.id
            #Facture cash
            if dette_controle_formulaire==False:
               flash('Etablir la facture','success')
               return redirect(url_for('vente.infofacture'))
            else:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.grosinfofacture'))

   #Ajourd'hui
   aujourd=date.today()
   date_format_avant=str(aujourd).split("-")
   date_formater="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])
   
   if request.method=='GET':
      form.codefacture.data = codefacture
      form.date_op.data=date_formater
      form.client_input_cherch.data=client_unique
   
   return render_template('vente/facture.html',option_encours=option_encours, title=title, form=form)

""" Terminer une facture"""
@vente.route('/annule_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def annulefacture():
   option_encours='vente'
   title='Vente'
   #Type de la vente
   type_validation_encours=utilitaire.validationtype()
   #Dette.
   dette_ver=utilitaire.validationtype_dette()
   cash_dette_encours=None
   #Controle de facture
   dette_controle_formulaire=None
   cash_dette_encours=None
   if type_validation_encours is None:
      #Controle de la facture de dette
      if dette_ver is None:
         pass
      else:
         if dette_ver==1:
            dette_controle_formulaire=True
         else:
            dette_controle_formulaire=False  
   else:
      if type_validation_encours==1:
         cash_dette_encours=True
      else:
         cash_dette_encours=False

   #Vérification de l'existence de la facture
   if utilitaire.verification_facture()==False:
      if cash_dette_encours != None:
         return redirect(url_for('vente.cash'))
      elif dette_controle_formulaire != None:
         return redirect(url_for('vente.dette'))

   else:
      code_facture=str(utilitaire.verification_facture())
      if cash_dette_encours != None:
         return redirect(url_for('vente.cash'))
      elif dette_controle_formulaire != None:
         return redirect(url_for('vente.dette'))

   return render_template('vente/facture.html',option_encours=option_encours, title=title, form=form)


""" Fin de la facture"""
@vente.route('/fin_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def finfacture(): 
   #Type de la vente
   type_validation_encours=utilitaire.validationtype()
   #Dette.
   dette_ver=utilitaire.validationtype_dette()
   cash_dette_encours=None
   #Controle de facture
   dette_controle_formulaire=None
   cash_dette_encours=None
   payement_facture_controle=None

   if 'annuler_facture' in session:
      payement_facture_controle=session['annuler_facture']

   # Flash de message
   
   if type_validation_encours is None:
      #Controle de la facture de dette
      if dette_ver is None:
         pass
      else:
         if dette_ver==1:
            dette_controle_formulaire=True
         else:
            dette_controle_formulaire=False  
   else:
      if type_validation_encours==1:
         cash_dette_encours=True
      else:
         cash_dette_encours=False

   if cash_dette_encours != None:
      flash('Facture établie avec succes','success')
      return redirect(url_for('vente.cash'))
   elif dette_controle_formulaire != None:
      flash('Facture établie avec succes','success')
      return redirect(url_for('vente.dette'))
   elif payement_facture_controle !=None:
      flash('Payement avec succes','success')
      return redirect(url_for('vente.dette'))


""" Suppression sur la facture"""
@vente.route('/annule/facture/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def supprimer_facture(facture):
    
   #NON ENVOIE DE PARAMETRE
   if facture is None:
      abort(404)
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))

   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first_or_404()
   # code de facture
   facture_type=[facture_encours.dette]
   copie_facture=facture_type.copy()


   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   # RETOUR DES PRODUITS AU STOCK AVEC SES VALEURS
   valeur_de_vente=Valeurvente.query.filter_by(facture_id=facture).all()
   # La variable comparée
   valeur_comparer=[]
   for val in valeur_de_vente:
      i=val.montants
      valeur_comparer.insert(0,i)
   
   #Valeur des ventes
   sommes_valeurs_comparer=sum(valeur_comparer)
   print(sommes_valeurs_comparer,'comparée de la facture -----------------------------')
   valeur_vente_somme=facture_encours.valeur_vendue

   if facture_encours.dette == True:
      if sommes_valeurs_comparer == valeur_vente_somme:
         pass
      else:
         flash("Cette facture est déjà encours de payement, impossible de l'annulée","danger")
         return redirect(url_for('vente.dette'))

   #Valeur de la vente
   if valeur_de_vente != []:
      for vente_facture_stock in valeur_de_vente:
         #Verification du solde de produit
         id_produit_boutique=vente_facture_stock.produitboutique_id
         ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_boutique, boutique_id=current_user.boutique_id, solde=True).first()
         ver_stock.solde=False
         #Retour de produit avec la valeur
         if vente_facture_stock.quantite != 0 and vente_facture_stock.quantite_s != 0:
            # Première valeur en stock
            quantite_un=vente_facture_stock.quantite 
            valeur_de_vente_un= float(vente_facture_stock.quantite ) * float(vente_facture_stock.prix_unitaire)
            
            stock_dsiponible_un=ver_stock.disponible + vente_facture_stock.quantite 
            valeur_de_stock_un= float(ver_stock.valeur_dispo) + valeur_de_vente_un

            #deuxième valeur de retour en stock
            quantite_deux=vente_facture_stock.quantite_s 
            valeur_de_vente_deux= float(vente_facture_stock.quantite_s ) * float(vente_facture_stock.prix_unitaire_s)
            
            stock_dsiponible_deux=stock_dsiponible_un+ vente_facture_stock.quantite_s 
            valeur_de_stock_deux= valeur_de_stock_un + valeur_de_vente_deux

            stockage_boutique_un=Stock(quantite=quantite_un, valeur=valeur_de_vente_un, datest=facture_encours.date, prix_unit=vente_facture_stock.prix_unitaire, 
                        disponible=stock_dsiponible_un, 
                        valeur_dispo=valeur_de_stock_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit_boutique)
            
            stockage_boutique_deux=Stock(quantite=quantite_deux, valeur=valeur_de_vente_deux, datest=facture_encours.date, prix_unit=vente_facture_stock.prix_unitaire_s, 
                        disponible=stock_dsiponible_deux, 
                        valeur_dispo=valeur_de_stock_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit_boutique, solde=True)
            
            db.session.add(stockage_boutique_un)
            db.session.add(stockage_boutique_deux)
         
         elif vente_facture_stock.quantite != 0 or vente_facture_stock.quantite_s != 0:
            if vente_facture_stock.quantite != 0:

               # Première valeur en stock
               quantite_un=vente_facture_stock.quantite 
               valeur_de_vente_un= float(vente_facture_stock.quantite ) * float(vente_facture_stock.prix_unitaire)
               
               stock_dsiponible_un=ver_stock.disponible + vente_facture_stock.quantite 
               valeur_de_stock_un= float(ver_stock.valeur_dispo) + valeur_de_vente_un

               stockage_boutique_un=Stock(quantite=quantite_un, valeur=valeur_de_vente_un, datest=facture_encours.date, prix_unit=vente_facture_stock.prix_unitaire, 
                        disponible=stock_dsiponible_un, 
                        valeur_dispo=valeur_de_stock_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit_boutique, solde=True)
               db.session.add(stockage_boutique_un)

            elif vente_facture_stock.quantite_s != 0:

               #deuxième valeur de retour en stock
               quantite_deux=vente_facture_stock.quantite_s 
               valeur_de_vente_deux= float(vente_facture_stock.quantite_s ) * float(vente_facture_stock.prix_unitaire_s)
               
               stock_dsiponible_deux=ver_stock.disponible + vente_facture_stock.quantite_s 
               valeur_de_stock_deux= float(ver_stock.valeur_dispo) + valeur_de_vente_deux

               stockage_boutique_deux=Stock(quantite=quantite_deux, valeur=valeur_de_vente_deux, datest=facture_encours.date, prix_unit=vente_facture_stock.prix_unitaire_s, 
                        disponible=stock_dsiponible_deux, 
                        valeur_dispo=valeur_de_stock_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit_boutique, solde=True)
            
               db.session.add(stockage_boutique_deux)
      #Commit de l'enregistrement
      db.session.commit()
   else:
      Facture.query.filter_by(id=facture, facture_user=current_user).delete()
      db.session.commit()

   #Vérification de la vente encours de la suppression
   vente_encours=Vente.query.filter_by(facture_id=facture).all()
   
   if vente_encours !=[]:
      for sup_facture in vente_encours:
         Vente.query.filter_by(id=sup_facture.id).delete()
         db.session.commit()
   
   #Supression des elements de la vente de valeur
   if valeur_de_vente != []:
      for i in valeur_de_vente:
         Valeurvente.query.filter_by(id=i.id).delete()
         db.session.commit()

   flash("La facture supprimer avec succès",'success')

   Facture.query.filter_by(id=facture, facture_user=current_user).delete()
   db.session.commit()

   if copie_facture[0] == True:
      return redirect(url_for('vente.dette'))
   else:
      return redirect(url_for('vente.cash'))

""" validation """
@vente.route('/validation/<int:type>')
@login_required
@autorisation_vendeur
def validation(type):  
   type_vente_encours=type
   vente_cash_detaille_facture=None
   if type_vente_encours is None:
      flash('Attention respect la procedure','danger')
      return redirect(url_for('vente.cash'))
   else:
      if type_vente_encours==1 or type_vente_encours==0:
         vente_cash_detaille_facture=type_vente_encours
         session['validation']=vente_cash_detaille_facture
         return redirect(url_for('vente.facturecash'))
      else:
         flash('Les parametres ne sont pas correctes','danger')
         return redirect(url_for('vente.cash'))


""" validation  de la dette"""
@vente.route('/validation/dette/<int:type>')
@login_required
@autorisation_vendeur
def validation_dette(type):  
   type_vente_encours=type
   vente_cash_detaille_facture=None
   if type_vente_encours is None:
      flash('Attention respect la procedure','danger')
      return redirect(url_for('vente.index'))
   else:
      if type_vente_encours==1 or type_vente_encours==0:
         vente_cash_detaille_facture=type_vente_encours
         session['validation_dette']=vente_cash_detaille_facture
         return redirect(url_for('vente.facturecash'))
      else:
         flash('Les parametres ne sont pas correctes','danger')
         return redirect(url_for('vente.dette'))


""" Facture acompte de la vente """
@vente.route('/validation_acompte/<int:type>')
@login_required
@autorisation_vendeur
def validation_acompte(type):  
   type_vente_encours=type
   vente_cash_detaille_facture=None
   if type_vente_encours is None:
      flash('Attention respect la procedure','danger')
      return redirect(url_for('vente.acompte'))
   else:
      if type_vente_encours==1 or type_vente_encours==0:
         vente_cash_detaille_facture=type_vente_encours
         session['validation_acompte']=vente_cash_detaille_facture
         return redirect(url_for('vente.factureacompte'))
      else:
         flash('Les parametres ne sont pas correctes','danger')
         return redirect(url_for('vente.acompte'))

""" Ajouter une facture"""
@vente.route('/facturation_acompte', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def factureacompte():
   option_encours='vente'
   title='Vente'
   #Code de la facture
   codefacture=utilitaire.codefacture()
   #Vérification de l'existence de la facture
   if utilitaire.verification_facture()==False:
      #return redirect(url_for('vente.acompte'))
      pass
   #Utilitaire
   client_unique=utilitaire.client_defautl()
   #Type de la vente facture acompte
   type_validation_encours=utilitaire.validationacompte()
   vente_acompte_validation=None

   if type_validation_encours is None:
      flash('Attention prière de suivre la procedure')
      #return redirect(url_for('vente.acompte'))
   else:
      if type_validation_encours == 1:
         vente_acompte_validation=True
      else:
         vente_acompte_validation=False

   #Formulaire
   form=FactureAcForm()
   #Enregistrement de la facture
   if form.validate_on_submit():
      client_nv=utilitaire.client_entree(form.client_input.data) #Enregistrement et retour clien
      code_fact_one=utilitaire.verification_facture() #Vérfication code de la facture
      #lecompte client
      clients=form.clients_client.data
      #Formatage de la date
      date_no_formater=str(form.date_op.data)
      date_format_avant=date_no_formater.split("-")
      date_operation="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0]) #La date formatée
      session["datefacture"]=date_operation
      #Enregistrement selon les information du client
      if client_nv is not None and form.client_input_cherch.data is not None:
         if vente_acompte_validation is not None:
            operation_facture=Facture(code_facture=code_fact_one,vente_acompte=True, compte_id=clients.id, date=date_operation, client_id=client_nv.id, user_id=current_user.id, boutique_id=current_user.boutique_id,type_vente=vente_acompte_validation)
            db.session.add(operation_facture)
            db.session.commit()
            session["idfacture"]=operation_facture.id
            session['client_compte']=clients.id
            #Facturation cash
            if vente_acompte_validation==False:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.infofactureacompte'))
            else:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.grosinfofactureacompte'))

      elif client_nv is None and form.client_input_cherch.data is not None :
         if vente_acompte_validation is not None:
            operation_facture=Facture(code_facture=code_fact_one,vente_acompte=True, compte_id=clients.id, date=date_operation, client_id=form.client_input_cherch.data.id, user_id=current_user.id, boutique_id=current_user.boutique_id, type_vente=vente_acompte_validation)
            db.session.add(operation_facture)
            db.session.commit()
            session["idfacture"]=operation_facture.id
            session['client_compte']=clients.id
            #Facture cash
            if vente_acompte_validation==False:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.infofactureacompte'))
            else:
               flash('Etablir la facture','success') 
               return redirect(url_for('vente.grosinfofactureacompte'))
   #Ajourd'hui
   aujourd=date.today()
   date_format_avant=str(aujourd).split("-")
   date_formater="{}-{}-{}".format(date_format_avant[2],date_format_avant[1],date_format_avant[0])
   
   if request.method=='GET':
      form.codefacture.data = codefacture
      form.date_op.data=date_formater
      form.client_input_cherch.data=client_unique
   
   return render_template('vente/facture_acompte.html',option_encours=option_encours, title=title, form=form)







#------------------------- ETABLISSEMENT DE LA FACTURE CASH DETAILLE ------------------------------------------

""" Les informations de la facture"""
@vente.route('/infos_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def infofacture():
   option_encours='vente'
   title='Vente'
   
   #FACTURE ETABLIE 
   id_facture=utilitaire.id_facture_client()
   date_facture=utilitaire.facture_date()

   if id_facture is None:
      return redirect(url_for('vente.facturecash'))

   #Formulaire de la facture
   form=VenteFactureForm()

   #ENREGISTREMENT DE LA VENTE SUR LA FACTURE
   if form.validate_on_submit():
      #LES VARIABLES PRINCIPALES
      prix_du_produit=form.prix_vente_detaille.data #Prix du produit
      quantite_vendu=form.quantite.data #Quantité
      produit_vendu =form.produit_vente.data # Produit vendu

      #OPERATION DE VERIFICATION DU STOCK DISPONIBLE
      stockage_produit=Stock.query.filter_by(produitboutique_id=produit_vendu.id, boutique_id=current_user.boutique_id, solde=True).first()   
      if stockage_produit.disponible < quantite_vendu:
         embal=utilitaire.emballage_taille(stockage_produit.disponible,quantite_vendu)
         flash('Attention le stock du produit {} et de {} {} '.format(produit_vendu.nom_produit, stockage_produit.disponible,embal),'danger')
         return redirect(url_for('vente.infofacture'))
      #OPERATION DE LA VENTE SUR LES VARIABLES
      #Prix de l'operation
      prix_op_vente=None
      if prix_du_produit==0:
         if produit_vendu.emballage == "Carton" or produit_vendu.emballage == "Box": 
            nbr_cont_pro=None
            if produit_vendu.nombre_contenu==0:
               nbr_cont_pro=1
            else:
               nbr_cont_pro=produit_vendu.nombre_contenu
            prix_op_vente=float(produit_vendu.vt_detaille_piece)   # Prix en fonction de produit
         else:
            prix_op_vente=produit_vendu.vt_detaille_piece
      else:
         prix_op_vente=prix_du_produit #Prix en fonction de la variation
      #Valeur de la transanction
      valeur_de_produit=float(prix_op_vente*quantite_vendu)

      #VARIABLES DES VALEURS DE VENTE
      prix_un=0
      prix_deux=0
      qte_un=0
      qte_deux=0
      
      # VALEUR DE LA MARCHANDISE VENDUE
      produit_non_perrisable=None #Les id des opértaions
      produit_perrisable_encours=None
      produits_anterieur=[]
      prix_valeur_marchandise=None
      valeur_vendue_marchandise=None
      disponible_totale=stockage_produit.disponible
      #Solde_disponible
      inv_prod_solde=Stock.query.filter(Stock.produitboutique_id==produit_vendu.id, Stock.solde==True).first_or_404()
            
      if produit_vendu is not None:
         if produit_vendu.perissable==True:
               produit_perrisable_encours=produit_vendu.id
         else:
               produit_non_perrisable=produit_vendu.id
                  
         if produit_perrisable_encours is not None:
               pro_per_sel=produit_perrisable_encours
               inv_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id, solde=False, stockage=True).order_by(Stock.id.desc()).limit(2)
               # Les produits antérieurs
               for prod_ant_par_produi in inv_produit_anterieur:
                  i=prod_ant_par_produi.id
                  produits_anterieur.insert(0,i)
               #Vérification si les deux produit recement stock sont là
               if len(produits_anterieur) > 1 :
                  stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                  stock_mouvement_dernier_mouvement=stc.quantite
                  differnce_de_la_dernier=disponible_totale - stock_mouvement_dernier_mouvement      
                  if differnce_de_la_dernier >= 0:
                     stock_anteieur= differnce_de_la_dernier - quantite_vendu
                     if stock_anteieur >=0:                   
                        valeur_vendue_marchandise=float(stc.prix_unit) * quantite_vendu
                        #Les données d'enregistrement sur les produits
                        prix_un=float(stc.prix_unit)
                        qte_un=quantite_vendu
                     else:
                        nouvelle_difference_value=quantite_vendu - differnce_de_la_dernier
                        val_une= float(differnce_de_la_dernier) * float(stc.prix_unit)
                        prix_d=Stock.query.filter_by(id=produits_anterieur[1]).first()
                        val_deux= float(nouvelle_difference_value) * float(prix_d.prix_unit)
                        valeur_vendue_marchandise=val_une + val_deux

                        #Les données d'enregistrement sur les produits
                        prix_un=float(stc.prix_unit)
                        qte_un=val_une
                        prix_deux=float(prix_d.prix_unit)
                        qte_deux=float(nouvelle_difference_value)
                  else:
                     prix_d=Stock.query.filter_by(id=produits_anterieur[1]).first()
                     valeur_vendue_marchandise=float(quantite_vendu) * float(prix_d.prix_unit)
                     #Les données d'enregistrement sur les produits
                     prix_un=float(prix_d.prix_unit)
                     qte_un=quantite_vendu
               # Stckage inferieur à un
               if len(produits_anterieur) == 1:
                  stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                  stock_mouvement_dernier_mouvement=stc.quantite
                  differnce_de_la_dernier=disponible_totale - stock_mouvement_dernier_mouvement      
                  if differnce_de_la_dernier >= 0:
                     stock_anteieur= differnce_de_la_dernier - quantite_vendu
                     if stock_anteieur >=0:
                        valeur_vendue_marchandise=float(stc.prix_unit) * quantite_vendu
                        #Les données des marchandises
                        prix_un=float(stc.prix_unit)
                        qte_un=val_une
                     else:
                        der_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id,stockage=True).order_by(Stock.id.desc()).first()
                        nouvelle_difference_value=quantite_vendu - differnce_de_la_dernier
                        val_une= float(differnce_de_la_dernier) * float(stc.prix_unit)
                        val_deux= float(nouvelle_difference_value) * float(der_produit_anterieur.prix_unit)
                        valeur_vendue_marchandise=val_une + val_deux

                        #Les données d'enregistrement sur les produits
                        
                        prix_un=float(stc.prix_unit)
                        qte_un=val_une
                        prix_deux=float(der_produit_anterieur.prix_unit)
                        qte_deux=float(nouvelle_difference_value)                        
                  else:
                     der_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id,stockage=True).order_by(Stock.id.desc()).first()
                     valeur_vendue_marchandise=float(quantite_vendu) * float(der_produit_anterieur.prix_unit)
                     #Les données du produits
                     prix_deux=float(der_produit_anterieur.prix_unit)
                     qte_deux=quantite_vendu
               if len(produits_anterieur) == 0:
                  der_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id, stockage=True).order_by(Stock.id.desc()).first()
                  valeur_vendue_marchandise=float(quantite_vendu) * float(der_produit_anterieur.prix_unit)
                  #Les données du produits
                  prix_deux=float(der_produit_anterieur.prix_unit)
                  qte_deux=quantite_vendu
                  
            #LES PRODUITS NON PERSSISABLE
         if produit_non_perrisable is not None:
            pro_per_sel=produit_perrisable_encours
            inv_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id, stockage=True).order_by(Stock.id.desc()).first()
            valeur_vendue_marchandise=float(quantite_vendu) * float(inv_produit_anterieur.prix_unit)
            #Les données du produits
            prix_un=float(inv_produit_anterieur.prix_unit)
            qte_un=quantite_vendu                 
         else:
               pass
      
      # VERIFICATION ET ENREGISTREMENT DE PRODUIT
      produits_valeur_vente=Valeurvente.query.filter_by(produitboutique_id=produit_vendu.id, facture_id=id_facture).first()
      montant_un= float(prix_un) *  float(qte_un)
      montant_deux= float(prix_deux) * float(qte_deux)
      montants=montant_un + montant_deux
      if produits_valeur_vente is None:
         valeur_vente_encours=Valeurvente(quantite=qte_un, quantite_s=qte_deux, prix_unitaire=prix_un, prix_unitaire_s=prix_deux, montant=montant_un,
                                          montant_s=montant_deux,montants=montants, produitboutique_id=produit_vendu.id, facture_id=id_facture)
         db.session.add(valeur_vente_encours)
         db.session.commit()
      else:
         produits_valeur_vente.quantite=produits_valeur_vente.quantite + qte_un
         produits_valeur_vente.quantite_s=produits_valeur_vente.quantite_s + qte_deux
         produits_valeur_vente.montant= float(produits_valeur_vente.montant) +float(montant_un) 
         produits_valeur_vente.montant_s=float(produits_valeur_vente.montant_s) + float(montant_deux)
         produits_valeur_vente.montants=float(produits_valeur_vente.montants) + float(montants)
         db.session.commit()

      #OPERATION DE STOCKAGE 
      stock_disponible_boutique=stockage_produit.disponible - quantite_vendu
      prix_unitaire_stock=stockage_produit.valeur_dispo/stockage_produit.disponible
      valeur_de_produit_sock=float(prix_unitaire_stock*stock_disponible_boutique)

      #ENREGISTREMENT DE LA VENTE ET MODIFICATION DU STOCKAGE
      

      #Vérification de la vente du produit sur la facture
      vente_facture=Vente.query.filter_by(facture_id=id_facture,produitboutique_id=produit_vendu.id).first()
      if vente_facture is None:
         #Enregistrement de la vente
         print('-------------------Vente1------------------------------')
         vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
         db.session.add(vente_sur_facture)
      else:
         print('-------------------Vente2------------------------------')
         if prix_op_vente==vente_facture.prix_unitaire:
            print('-------------------Vente3------------------------------')
            mm_facture_qte=float(vente_facture.quantite) + float(quantite_vendu)
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 1', mm_facture_qte)

            mm_facture_valeur=float(vente_facture.montant) + float(valeur_de_produit)
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 2', mm_facture_valeur)
            #Nouveau prix et nouvelle quantité
            vente_facture.quantite=mm_facture_qte
            vente_facture.montant=mm_facture_valeur
            
         else:
            print('-------------------Vente4------------------------------')
            vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
            db.session.add(vente_sur_facture)

      # Mise à jour du stock
      stockage_produit.solde=False
      stockage_boutique=Stock(quantite=quantite_vendu, valeur=valeur_de_produit, datest=date_facture, prix_unit=prix_op_vente, 
                           disponible=stock_disponible_boutique, 
                           valeur_dispo=valeur_de_produit_sock, vente_boutique=True, boutique_id=current_user.boutique_id, 
                           stock_user=current_user, produitboutique_id=produit_vendu.id, solde=True)
      db.session.add(stockage_boutique)

      # MISE A JOUR DE LA FACTURE
      mise_jr_facture=Facture.query.filter_by(id=id_facture).first()
      if mise_jr_facture.montant is None:
         mise_jr_facture.montant=valeur_de_produit
         mise_jr_facture.valeur_vendue=valeur_vendue_marchandise
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant ) + valeur_de_produit
         mise_jr_facture.valeur_vendue=float(mise_jr_facture.valeur_vendue) + float(valeur_vendue_marchandise)
      #Enregistrement et mise à des opération
      db.session.commit()
      embal=utilitaire.emballage_taille(stockage_produit.disponible,quantite_vendu)
      flash('Vous avez ajouté {} et de {} {} '.format(produit_vendu.nom_produit, quantite_vendu,embal),'success')
      return redirect(url_for('vente.infofacture'))

   # INJECTION DANS LE FORMULAIRE
   if request.method=='GET':
      x=0
      x=float(x)
      form.prix_vente_detaille.data=x
   
   #LA FACTURE ENCOURS D'ETABLISSEMENT
   facture_encours_etablie=Vente.query.filter_by(facture_id=id_facture,no_facture=False).all()
   facture_donnes=Facture.query.filter_by(id=id_facture).first()
   ver_facture_encours="Vide"
   if facture_encours_etablie is not None:
      ver_facture_encours="NoVide"
   
   #DIMIUTION SUR LA FACTURE
   dimunition=DiminutionFactureForm()

   return render_template('vente/vente_cash_detaille.html',dimunition=dimunition,facture_d=facture_donnes,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, option_encours=option_encours, title=title, form=form, id_facture=id_facture)


""" Diminution de la facture"""
@vente.route('/dim-<int:facture>/<int:vente>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def fact_dim(facture,vente):
   #FORMULAIRE DE DIMUTION
   dimunition=DiminutionFactureForm()
   
   #NON ENVOIE DE PARAMETRE
   if facture is None and vente is None :
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofacture'))

   #OPERATION DE DIMINUTION ENCOURS
   if dimunition.validate_on_submit():
      facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first()
      #Vérification de l'existence de la facture pour le client
      if facture_encours is None:
         flash("Attention cette opération est dangereuse","danger")
         return redirect(url_for('vente.infofacture'))

      #Quantité à diminuer dans la facture
      quantite=dimunition.d_quantite.data
      #Vérification de la vente encours
      vente_encours=Vente.query.filter_by(id=vente,facture_id=facture).first()
      # VERIFICATION DES VENTES PRECEDENTES
      id_pro_valeurs=vente_encours.produitboutique_id
      ver_vente_valeur=Valeurvente.query.filter_by(produitboutique_id=id_pro_valeurs, facture_id=facture).first()

      valeur_entree_sous=quantite * vente_encours.prix_unitaire

      #DIMINUTION PROPREMENDITE
      if vente_encours.quantite >=quantite:
         #SOCK DISPONIBLE
         id_produit_encours=vente_encours.produitboutique_id
         ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_encours, boutique_id=current_user.boutique_id, solde=True).first()
         ver_stock.solde=False

         # Opération des ventes
         if ver_vente_valeur is not None:
            if ver_vente_valeur.quantite != 0 and ver_vente_valeur.quantite_s != 0:
               premiere_valeur = ver_vente_valeur.quantite - quantite
               if premiere_valeur < 0:
                  premier_valeur_correct= ver_vente_valeur.quantite
                  deuxieme_valeur_correct= quantite - ver_vente_valeur.quantite
                  #Valeur des ventes 
                  montant_pre=premier_valeur_correct * ver_vente_valeur.prix_unitaire
                  montant_de=deuxieme_valeur_correct * ver_vente_valeur.prix_unitaire_s
                  #Total montant
                  montant_total= montant_pre + montant_de
                  #Reste de la valeur de vente
                  reste_sur_vente= ver_vente_valeur.quantite_s - deuxieme_valeur_correct
                  valeur_reste= reste_sur_vente * ver_vente_valeur.prix_unitaire_s

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite = 0 
                  ver_vente_valeur.quantite_s = reste_sur_vente
                  ver_vente_valeur.montant = 0
                  ver_vente_valeur.montant_s = valeur_reste
                  ver_vente_valeur.prix_unitaire = 0
                  ver_vente_valeur.montants = valeur_reste

                  #Enregistrement de stock
                  disponible_un= ver_stock.disponible + premier_valeur_correct
                  valeur_dispo_un= float(ver_stock.valeur_dispo) + float(montant_pre) 

                  disponible_deux= disponible_un + deuxieme_valeur_correct
                  valeur_dispo_deux= valeur_dispo_un + float(montant_de)


                  stockage_boutique_un=Stock(quantite=premier_valeur_correct, valeur=montant_pre, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire, 
                                    disponible=disponible_un, 
                                    valeur_dispo=valeur_dispo_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours)

                  stockage_boutique_deux=Stock(quantite=deuxieme_valeur_correct, valeur=montant_de, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire_s, 
                                    disponible=disponible_deux, 
                                    valeur_dispo=valeur_dispo_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
                  db.session.add(stockage_boutique_un)
                  db.session.add(stockage_boutique_deux)

                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(montant_total)
               else:
                  premier_valeur_correct= ver_vente_valeur.quantite - quantite
                  qte_de_op=float(quantite)
                  #Valeur des ventes 
                  montant_pre=premier_valeur_correct * ver_vente_valeur.prix_unitaire
                  valeu_de_op=qte_de_op * float(ver_vente_valeur.prix_unitaire)

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite = premier_valeur_correct 
                  ver_vente_valeur.montant = montant_pre
                  ver_vente_valeur.montants = float(ver_vente_valeur.montants) - float(montant_pre)

                  #Enregistrement de stock
                  disponible_un= ver_stock.disponible + quantite
                  valeur_dispo_un= float(ver_stock.valeur_dispo) + float(valeu_de_op) 

                  stockage_boutique_un=Stock(quantite=qte_de_op, valeur=valeu_de_op, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire, 
                                    disponible=disponible_un, 
                                    valeur_dispo=valeur_dispo_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

                  db.session.add(stockage_boutique_un)
                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(valeu_de_op)
            elif ver_vente_valeur.quantite != 0 or ver_vente_valeur.quantite_s !=0:
               if ver_vente_valeur.quantite != 0 :
                  premier_valeur_correct= ver_vente_valeur.quantite - quantite
                  qte_de_op=float(quantite)
                  #Valeur des ventes 
                  montant_pre=premier_valeur_correct * ver_vente_valeur.prix_unitaire
                  valeu_de_op=qte_de_op * float(ver_vente_valeur.prix_unitaire)

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite = premier_valeur_correct 
                  ver_vente_valeur.montant = montant_pre
                  ver_vente_valeur.montants = float(ver_vente_valeur.montants) - float(montant_pre)

                  #Enregistrement de stock
                  disponible_un= ver_stock.disponible + quantite
                  valeur_dispo_un= float(ver_stock.valeur_dispo) + float(valeu_de_op) 

                  stockage_boutique_un=Stock(quantite=qte_de_op, valeur=valeu_de_op, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire, 
                                    disponible=disponible_un, 
                                    valeur_dispo=valeur_dispo_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

                  db.session.add(stockage_boutique_un)
                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(valeu_de_op)
               elif ver_vente_valeur.quantite_s != 0 :
                  deuxieme_valeur_correct= ver_vente_valeur.quantite_s - quantite
                  qte_de_op=float(quantite)
                  #Valeur des ventes 
                  montant_de=deuxieme_valeur_correct * ver_vente_valeur.prix_unitaire_s
                  valeu_de_op=qte_de_op * float(ver_vente_valeur.prix_unitaire_s)

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite_s = deuxieme_valeur_correct 
                  ver_vente_valeur.montant_s = montant_de
                  ver_vente_valeur.montants = float(ver_vente_valeur.montants) - float(montant_de)

                  #Enregistrement de stock
                  disponible_deux= ver_stock.disponible + quantite
                  valeur_dispo_deux= float(ver_stock.valeur_dispo) + float(valeu_de_op) 

                  stockage_boutique_deux=Stock(quantite=qte_de_op, valeur=valeu_de_op, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire_s, 
                                    disponible=disponible_deux, 
                                    valeur_dispo=valeur_dispo_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

                  db.session.add(stockage_boutique_deux)
                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(valeu_de_op)
               
         # Traitement des quantités sur l'opération de vente
         quantite_vente_encours=vente_encours.quantite
         quantite_entree = quantite
         #Soustraction
         nouvelle_quantite=quantite_vente_encours - quantite_entree
         nv=nouvelle_quantite * vente_encours.prix_unitaire
         valeur=nv
         #Enregistrement de la diminution de la vente
         vente_encours.quantite=nouvelle_quantite
         vente_encours.montant=valeur

         #FACTURE ENCOURS
         nv_f=facture_encours.montant - valeur_entree_sous
         #Soustraction
         facture_encours.montant=nv_f

         #COMMIT DES OPERATION
         db.session.commit()

         flash("Vous avez diminuer une quantité de {}".format(quantite),"success")
         return redirect(url_for('vente.infofacture'))
      else:
         flash("Vous avez une quantité de {}".format(vente_encours.quantite),"danger")
         return redirect(url_for('vente.infofacture'))
   return render_template('vente/facture.html')


""" Suppression sur la facture"""
@vente.route('/sup-<int:facture>/<int:vente>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def fact_sup(facture,vente):
    
   #NON ENVOIE DE PARAMETRE
   if facture is None and vente is None :
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofacture'))
   
   #Type de la vente
   type_validation_encours=utilitaire.validationtype()
   encours_dette_validation=utilitaire.validationtype_dette()
   cash_dette_encours=None
   dette_encours_sup=None


   if type_validation_encours is None:
      if encours_dette_validation==1:
         dette_encours_sup=True
      else:
         dette_encours_sup=False
   else:
      if type_validation_encours==1:
         cash_dette_encours=True
      else:
         cash_dette_encours=False

   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first()
   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofacture'))
   
   #Vérification de la vente encours
   vente_encours=Vente.query.filter_by(id=vente,facture_id=facture).first()

   #Quantité à diminuer dans la facture
   quantite=vente_encours.quantite

   #DIMINUTION PROPREMENDITE

   quantite_vente_encours=vente_encours.quantite
   quantite_entree = quantite
   #Soustraction
   nouvelle_quantite=quantite_vente_encours - quantite_entree
   nv=quantite* vente_encours.prix_unitaire
   valeur=nv
   #Enregistrement de la diminution de la vente
   vente_encours.quantite=nouvelle_quantite
   vente_encours.montant=valeur
   vente_encours.no_facture=True

   #FACTURE ENCOURS
   nv_f=facture_encours.montant - valeur
   valeur_facture=nv_f 
   #Soustraction
   facture_encours.montant=valeur_facture

   #SOCK DISPONIBLE
   id_produit_encours=vente_encours.produitboutique_id
   ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_encours, boutique_id=current_user.boutique_id, solde=True).first()
   ver_stock.solde=False
   #Les variable de stockage
   qte_stock_encours=ver_stock.disponible + quantite
   quantite_valeur_op=quantite*vente_encours.prix_unitaire # La valeur de l'opération
   valeurs_nouvelle_dispo= ver_stock.valeur_dispo + quantite_valeur_op

   #SUPPRESSION DES PRODUITS SUR LA FACTURE EN TENANT COMPTE DES VALEURS
   ver_valeur_stockage=Valeurvente.query.filter_by(facture_id=facture, produitboutique_id=id_produit_encours).first()
   if ver_valeur_stockage is not None:
      if ver_valeur_stockage.quantite != 0 and ver_valeur_stockage.quantite_s != 0:
         qte_disponible=ver_stock.disponible
         montant_un = float(ver_valeur_stockage.quantite) * float(ver_valeur_stockage.prix_unitaire)
         montant_deux= float(ver_valeur_stockage.quantite_s) * float(ver_valeur_stockage.prix_unitaire_s)

         nv_st_produi_un= qte_disponible + ver_valeur_stockage.quantite
         valeur_stock_un = float(ver_stock.valeur_dispo) + montant_un

         nv_st_produi_deux= nv_st_produi_un + ver_valeur_stockage.quantite_s
         valeur_stock_deux= valeur_stock_un + montant_deux

         #ENREGISTREMENT STOCKAGE DU PRODUIT
         stockage_boutique_un=Stock(quantite=ver_valeur_stockage.quantite, valeur=montant_un, datest=facture_encours.date,
                     prix_unit=ver_valeur_stockage.prix_unitaire, 
                     disponible=nv_st_produi_un, 
                     valeur_dispo=valeur_stock_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                     stock_user=current_user, produitboutique_id=id_produit_encours)
         
         stockage_boutique_deux=Stock(quantite=ver_valeur_stockage.quantite_s, valeur=montant_deux, datest=facture_encours.date,
                     prix_unit=ver_valeur_stockage.prix_unitaire_s, 
                     disponible=nv_st_produi_deux, 
                     valeur_dispo=valeur_stock_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                     stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

         db.session.add(stockage_boutique_un)
         db.session.add(stockage_boutique_deux)

         #SUPRESSION DE LA VALEUR SUR LA FACTURE
         montant_vendue=ver_valeur_stockage.montants
         facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(montant_vendue)
         #SUPRESSION DES CETTE ENTREES DANS LA VENTE
         Valeurvente.query.filter_by(facture_id=facture, produitboutique_id=id_produit_encours).delete()
      elif ver_valeur_stockage.quantite != 0 or ver_valeur_stockage.quantite_s != 0 :
         if ver_valeur_stockage.quantite != 0 :
            qte_disponible=ver_stock.disponible
            montant_un = float(ver_valeur_stockage.quantite) * float(ver_valeur_stockage.prix_unitaire)

            nv_st_produi_un= qte_disponible + ver_valeur_stockage.quantite
            valeur_stock_un = float(ver_stock.valeur_dispo) + montant_un

            #ENREGISTREMENT STOCKAGE DU PRODUIT
            stockage_boutique_un=Stock(quantite=ver_valeur_stockage.quantite, valeur=montant_un, datest=facture_encours.date,
                     prix_unit=ver_valeur_stockage.prix_unitaire, 
                     disponible=nv_st_produi_un, 
                     valeur_dispo=valeur_stock_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                     stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

            db.session.add(stockage_boutique_un)

            #SUPRESSION DE LA VALEUR SUR LA FACTURE
            montant_vendue=ver_valeur_stockage.montants
            facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(montant_vendue)
            #SUPRESSION DES CETTE ENTREES DANS LA VENTE
            Valeurvente.query.filter_by(facture_id=facture, produitboutique_id=id_produit_encours).delete()

         elif ver_valeur_stockage.quantite_s != 0:
            qte_disponible=ver_stock.disponible
            montant_deux= float(ver_valeur_stockage.quantite_s) * float(ver_valeur_stockage.prix_unitaire_s)

            nv_st_produi_deux= qte_disponible + ver_valeur_stockage.quantite_s
            valeur_stock_deux= montant_deux

            stockage_boutique_deux=Stock(quantite=ver_valeur_stockage.quantite_s, valeur=montant_deux, datest=facture_encours.date,
                     prix_unit=ver_valeur_stockage.prix_unitaire_s, 
                     disponible=nv_st_produi_deux, 
                     valeur_dispo=valeur_stock_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                     stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
            
            db.session.add(stockage_boutique_deux)

            #SUPRESSION DE LA VALEUR SUR LA FACTURE
            montant_vendue=ver_valeur_stockage.montants
            facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(montant_vendue)
            #SUPRESSION DES CETTE ENTREES DANS LA VENTE
            Valeurvente.query.filter_by(facture_id=facture, produitboutique_id=id_produit_encours).delete()
   else:
      pass
   #COMMIT DE TOUS LES ENREGISTREMENTS EN STOCKS
   db.session.commit()
   #SUPRESSION DE LA FACTURE
   flash("Vous avez supprime le {} sur la facture".format(vente_encours.vente_produitboutique.nom_produit),"success")
   Vente.query.filter_by(id=vente,facture_id=facture).delete()
   db.session.commit()
   if cash_dette_encours==False:
      return redirect(url_for('vente.infofacture'))
   else:
      return redirect(url_for('vente.grosinfofacture'))


""" Suppression sur la facture"""
@vente.route('/acompte/sup-<int:facture>/<int:vente>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def fact_sup_acompte(facture,vente):
    
   #NON ENVOIE DE PARAMETRE
   if facture is None and vente is None :
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofacture'))
   
   #Type de la vente
   type_validation_encours=utilitaire.validationtype()
   encours_dette_validation=utilitaire.validationtype_dette()
   cash_dette_encours=None
   dette_encours_sup=None


   if type_validation_encours is None:
      if encours_dette_validation==1:
         dette_encours_sup=True
      else:
         dette_encours_sup=False
   else:
      if type_validation_encours==1:
         cash_dette_encours=True
      else:
         cash_dette_encours=False

   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first()
   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofacture'))
   
   #Vérification de la vente encours
   vente_encours=Vente.query.filter_by(id=vente,facture_id=facture).first()

   #Quantité à diminuer dans la facture
   quantite=vente_encours.quantite

   #DIMINUTION PROPREMENDITE

   quantite_vente_encours=vente_encours.quantite
   quantite_entree = quantite
   #Soustraction
   nouvelle_quantite=quantite_vente_encours - quantite_entree
   nv=quantite * vente_encours.prix_unitaire
   valeur=nv
   #Enregistrement de la diminution de la vente
   vente_encours.quantite=nouvelle_quantite
   vente_encours.montant=valeur
   vente_encours.no_facture=True
   #FACTURE DES 
   id_prod_op=Valeurvente.query.filter_by(produitboutique_id=vente_encours.produitboutique_id, facture_id=facture).first()
   montants=id_prod_op.montants

   #FACTURE ENCOURS
   nv_f=facture_encours.montant - valeur
   valeur_facture=nv_f 
   #Soustraction
   facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(montants)
   facture_encours.montant=valeur_facture
   Vente.query.filter_by(id=vente,facture_id=facture).delete()
   Valeurvente.query.filter_by(produitboutique_id=vente_encours.produitboutique_id, facture_id=facture).delete()
   flash("Vous avez supprime le {} sur la facture".format(vente_encours.vente_produitboutique.nom_produit),"success")
   db.session.commit()
   
   if cash_dette_encours==False:
      return redirect(url_for('vente.infofactureacompte'))
   else:
      return redirect(url_for('vente.infofactureacompte'))

""" Impression facture"""
@vente.route('/imp-<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def impression(facture):

   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()
   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofacture'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/imprimer.html',facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)


""" Liste des factures """
@vente.route('/', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def index():  
   #Liste des factures
   option_encours='vente'
   title='Les factures'
   #Suppression de session
   session.pop('idfacture', None)
   session.pop('datefacture', None)
   session.pop('validation', None)
   session.pop('validation_dette', None)

   page= request.args.get('page', 1, type=int)
   list_facture=Facture.query.filter(Facture.annule==False).order_by(Facture.id.desc()).paginate(page=page, per_page=50)
   ver_facture_sub="Vide"
   liste_donne=None
   form=RechercheFactureForm()
   if form.validate_on_submit():
      code_id_facture=form.facture_client.data.id
      liste_donne=Facture.query.filter_by(id=code_id_facture).first()
      ver_facture_sub="NoVide" 
   return render_template('vente/index.html', form=form, liste=liste_donne, ver_facture_sub=ver_facture_sub, title=title, listes=list_facture, option_encours=option_encours)

""" Liste des factures cash"""
@vente.route('/cash', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def cash():  
   #Liste des factures
   option_encours='vente'
   title='Les factures'
   form=RechercheFactureForm()
   page= request.args.get('page', 1, type=int)
   list_facture=None
   #Suppression de session
   session.pop('idfacture', None)
   session.pop('datefacture', None)
   session.pop('validation', None)
   session.pop('validation_dette', None)

   #Session de supression de la facture sur la plateforme
   session['annuler_facture']=True

   list_facture=Facture.query.filter(Facture.cash==True, Facture.montant >=1, Facture.annule==False).order_by(Facture.id.desc()).paginate(page=page, per_page=50)
   ver_facture_sub="Vide"
   liste_donne=None
   if form.validate_on_submit():
      code_id_facture=form.facture_client.data.id
      liste_donne=Facture.query.filter_by(id=code_id_facture).first()
      ver_facture_sub="NoVide" 
   return render_template('vente/cash.html',form=form, liste=liste_donne, title=title, ver_facture_sub=ver_facture_sub, listes=list_facture, option_encours=option_encours)

""" Voir la facture"""
@vente.route('/voir/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def voir_facture(facture):
   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()
   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/voir_facture.html',facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)

""" Voir la facture"""
@vente.route('/voir/gros/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def voir_facture_gros(facture):
   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()
   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/voir_facture_gros.html',facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)


""" Voir la facture"""
@vente.route('/voir/imprimer/cash/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def voir_facture_gros_imprime(facture):
   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()
   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/voir_fa_imp_gros.html',facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)



""" Voir la facture"""
@vente.route('/voir/dette/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def voir_facture_paye(facture):
   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()

   payement_facture_etablie=Payement.query.filter_by(facture_id=facture).all()
   nombre_total_payer=[]
   nbr_tot_payer=None
   for i in payement_facture_etablie:
      a=i.montant
      nombre_total_payer.insert(0,a)
   nbr_tot_payer=sum(nombre_total_payer)

   nombre_total_dette=[]
   nbr_tot_dette=None
   for fac in facture_encours_etablie:
      a=fac.montant
      nombre_total_dette.insert(0,a)
   nbr_tot_dette=sum(nombre_total_dette)

   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/voir_facture_paye.html',nbr_tot_dette=nbr_tot_dette, payements=payement_facture_etablie, nbr_tot_payer=nbr_tot_payer, facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)



""" Voir la facture en gros de la dette"""
@vente.route('/voir/gros/dette/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def voir_facture_gros_paye(facture):
   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()

   payement_facture_etablie=Payement.query.filter_by(facture_id=facture).all()
   nombre_total_payer=[]
   nbr_tot_payer=None
   for i in payement_facture_etablie:
      a=i.montant
      nombre_total_payer.insert(0,a)
   nbr_tot_payer=sum(nombre_total_payer)

   nombre_total_dette=[]
   nbr_tot_dette=None
   for fac in facture_encours_etablie:
      a=fac.montant
      nombre_total_dette.insert(0,a)
   nbr_tot_dette=sum(nombre_total_dette)

   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/voir_facture_gros_paye.html',nbr_tot_dette=nbr_tot_dette, payements=payement_facture_etablie, nbr_tot_payer=nbr_tot_payer,facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)


""" Voir la facture"""
@vente.route('/voir/imprimer/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur_gerant
def voir_facture_imp(facture):
   title="Impression"
   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture).first_or_404()
   facture_encours_etablie=Vente.query.filter_by(facture_id=facture_encours.id,no_facture=False).all()

   payement_facture_etablie=Payement.query.filter_by(facture_id=facture).all()
   nombre_total_payer=[]
   nbr_tot_payer=None
   for i in payement_facture_etablie:
      a=i.montant
      nombre_total_payer.insert(0,a)
   nbr_tot_payer=sum(nombre_total_payer)

   nombre_total_dette=[]
   nbr_tot_dette=None
   for fac in facture_encours_etablie:
      a=fac.montant
      nombre_total_dette.insert(0,a)
   nbr_tot_dette=sum(nombre_total_dette)

   #Vérification de l'existence de la facture pour le client
   ver_facture_encours="Vide"
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   else:
      ver_facture_encours="NoVide"
   return render_template('vente/imprimer_dette.html',nbr_tot_dette=nbr_tot_dette, payements=payement_facture_etablie, nbr_tot_payer=nbr_tot_payer, facture_d=facture_encours,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, title=title)




# ------------------ LES INFORMARTIONS DE LA VENTE CASH  GROS --------------------------------------------

""" Les informations de la facture en gros"""
@vente.route('/gros_infos_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def grosinfofacture():
   option_encours='vente'
   title='Vente'
   
   #FACTURE ETABLIE 
   id_facture=utilitaire.id_facture_client()
   date_facture=utilitaire.facture_date()

   if id_facture is None:
      return redirect(url_for('vente.facturecash'))

   #Formulaire de la facture
   form=VenteFactureGForm()

   #ENREGISTREMENT DE LA VENTE SUR LA FACTURE
   if form.validate_on_submit():
      #LES VARIABLES PRINCIPALES
      prix_du_produit=form.prix_vente_gros.data #Prix du produit
      produit_vendu =form.produit_vente.data # Produit vendu
      nombre_de_quantite=form.quantite.data
      # DETERMINATION DES QUANTITES EN GROS
      quantite_vendu=None 
      ratio_de_nomination=None
      quantite_par_produit=produit_vendu.nombre_contenu #Nombre de produit par emballage
      nomination_de_quantite=form.nomination.data #Nomination de la quantité
      #Determination de ratio
      if nomination_de_quantite=='Quart':
         ratio_de_nomination=0.25
      elif nomination_de_quantite=='Demi':
         ratio_de_nomination=0.5
      else:
         ratio_de_nomination=1
      
      #Determination de la quantité
      if quantite_par_produit== 0 or quantite_par_produit== 1:
         quantite_vendu= 1 * nombre_de_quantite
      else:
         quantite_vendu=(quantite_par_produit * ratio_de_nomination) * nombre_de_quantite
         
      #OPERATION DE VERIFICATION DU STOCK DISPONIBLE
      stockage_produit=Stock.query.filter_by(produitboutique_id=produit_vendu.id, boutique_id=current_user.boutique_id, solde=True).first()
      
      nbr_quantite_notification=None
      if stockage_produit.disponible < quantite_vendu:
         if produit_vendu.emballage == 'Carton' or produit_vendu.emballage == 'Box':
            if quantite_par_produit== 0 or quantite_par_produit== 1:
               nbr_quantite_notification=(stockage_produit.disponible/1)
               flash('Attention le stock du produit {} est de {} {} '.format(produit_vendu.nom_produit, nbr_quantite_notification,produit_vendu.emballage),'danger')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               if produit_vendu.emballage == 'Carton':
                  nbr_quantite_notification=round(stockage_produit.disponible/quantite_par_produit,1)
                  flash('Attention le stock du produit {} est de {} {}s '.format(produit_vendu.nom_produit, nbr_quantite_notification,produit_vendu.emballage),'danger')
                  return redirect(url_for('vente.grosinfofacture'))
               else:
                  nbr_quantite_notification=round(stockage_produit.disponible/quantite_par_produit,1)
                  flash('Attention le stock du produit {} est de {} {} '.format(produit_vendu.nom_produit, nbr_quantite_notification,produit_vendu.emballage),'danger')
                  return redirect(url_for('vente.grosinfofacture'))
         else:
            if stockage_produit.disponible > 1 :
               nbr_quantite_notification=stockage_produit.disponible
               flash('Attention le stock du produit {} est de {}  Pièce '.format(produit_vendu.nom_produit, nbr_quantite_notification),'danger')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               flash('Attention le stock du produit {} est de {}  Pièces '.format(produit_vendu.nom_produit, nbr_quantite_notification),'danger')
               return redirect(url_for('vente.grosinfofacture'))
   
      #OPERATION DE LA VENTE SUR LES VARIABLES
      #Prix de l'operation
      prix_op_vente=None

      if prix_du_produit==0:
         if produit_vendu.emballage == "Carton" or produit_vendu.emballage == "Box": 
            nbr_cont_pro=None
            if produit_vendu.nombre_contenu==0:
               nbr_cont_pro=1
            else:
               nbr_cont_pro=produit_vendu.nombre_contenu
            prix_op_vente=float(produit_vendu.vt_gros_entier/nbr_cont_pro)   # Prix en fonction de produit
         else:
            prix_op_vente=produit_vendu.vt_gros_entier 
      else:
         prix_op_vente=prix_du_produit #Prix en fonction de la variation
      #Valeur de la transanction
      valeur_de_produit=float(prix_op_vente*quantite_vendu)

      #VARIABLES DES VALEURS DE VENTE
      prix_un=0
      prix_deux=0
      qte_un=0
      qte_deux=0
      
      # VALEUR DE LA MARCHANDISE VENDUE
      produit_non_perrisable=None #Les id des opértaions
      produit_perrisable_encours=None
      produits_anterieur=[]
      prix_valeur_marchandise=None
      valeur_vendue_marchandise=None
      disponible_totale=stockage_produit.disponible
      #Solde_disponible
      inv_prod_solde=Stock.query.filter(Stock.produitboutique_id==produit_vendu.id, Stock.solde==True).first_or_404()
      
      if produit_vendu is not None:
         if produit_vendu.perissable==True:
               produit_perrisable_encours=produit_vendu.id
         else:
               produit_non_perrisable=produit_vendu.id
                  
         if produit_perrisable_encours is not None:
               pro_per_sel=produit_perrisable_encours
               inv_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id, solde=False, stockage=True).order_by(Stock.id.desc()).limit(2)
               # Les produits antérieurs
               for prod_ant_par_produi in inv_produit_anterieur:
                  i=prod_ant_par_produi.id
                  produits_anterieur.insert(0,i)
               #Vérification si les deux produit recement stock sont là
               if len(produits_anterieur) > 1 :
                  stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                  stock_mouvement_dernier_mouvement=stc.quantite
                  differnce_de_la_dernier=disponible_totale - stock_mouvement_dernier_mouvement      
                  if differnce_de_la_dernier >= 0:
                     stock_anteieur= differnce_de_la_dernier - quantite_vendu
                     if stock_anteieur >=0:                   
                        valeur_vendue_marchandise=float(stc.prix_unit) * quantite_vendu
                        #Les données d'enregistrement sur les produits
                        prix_un=float(stc.prix_unit)
                        qte_un=quantite_vendu
                     else:
                        nouvelle_difference_value=quantite_vendu - differnce_de_la_dernier
                        val_une= float(differnce_de_la_dernier) * float(stc.prix_unit)
                        prix_d=Stock.query.filter_by(id=produits_anterieur[1]).first()
                        val_deux= float(nouvelle_difference_value) * float(prix_d.prix_unit)
                        valeur_vendue_marchandise=val_une + val_deux

                        #Les données d'enregistrement sur les produits
                        prix_un=float(stc.prix_unit)
                        qte_un=val_une
                        prix_deux=float(prix_d.prix_unit)
                        qte_deux=float(nouvelle_difference_value)
                  else:
                     prix_d=Stock.query.filter_by(id=produits_anterieur[1]).first()
                     valeur_vendue_marchandise=float(quantite_vendu) * float(prix_d.prix_unit)
                     #Les données d'enregistrement sur les produits
                     prix_un=float(prix_d.prix_unit)
                     qte_un=quantite_vendu
               # Stckage inferieur à un
               if len(produits_anterieur) == 1:
                  stc=Stock.query.filter_by(id=produits_anterieur[0]).first()
                  stock_mouvement_dernier_mouvement=stc.quantite
                  differnce_de_la_dernier=disponible_totale - stock_mouvement_dernier_mouvement      
                  if differnce_de_la_dernier >= 0:
                     stock_anteieur= differnce_de_la_dernier - quantite_vendu
                     if stock_anteieur >=0:
                        valeur_vendue_marchandise=float(stc.prix_unit) * quantite_vendu
                        #Les données des marchandises
                        prix_un=float(stc.prix_unit)
                        qte_un=val_une
                     else:
                        der_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id,stockage=True).order_by(Stock.id.desc()).first()
                        nouvelle_difference_value=quantite_vendu - differnce_de_la_dernier
                        val_une= float(differnce_de_la_dernier) * float(stc.prix_unit)
                        val_deux= float(nouvelle_difference_value) * float(der_produit_anterieur.prix_unit)
                        valeur_vendue_marchandise=val_une + val_deux

                        #Les données d'enregistrement sur les produits
                        
                        prix_un=float(stc.prix_unit)
                        qte_un=val_une
                        prix_deux=float(der_produit_anterieur.prix_unit)
                        qte_deux=float(nouvelle_difference_value)                        
                  else:
                     der_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id,stockage=True).order_by(Stock.id.desc()).first()
                     valeur_vendue_marchandise=float(quantite_vendu) * float(der_produit_anterieur.prix_unit)
                     #Les données du produits
                     prix_deux=float(der_produit_anterieur.prix_unit)
                     qte_deux=quantite_vendu
               if len(produits_anterieur) == 0:
                  der_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id, stockage=True).order_by(Stock.id.desc()).first()
                  valeur_vendue_marchandise=float(quantite_vendu) * float(der_produit_anterieur.prix_unit)
                  #Les données du produits
                  prix_deux=float(der_produit_anterieur.prix_unit)
                  qte_deux=quantite_vendu
                  
            #LES PRODUITS NON PERSSISABLE
         if produit_non_perrisable is not None:
            pro_per_sel=produit_perrisable_encours
            inv_produit_anterieur=Stock.query.filter_by(produitboutique_id=produit_vendu.id, stockage=True).order_by(Stock.id.desc()).first()
            valeur_vendue_marchandise=float(quantite_vendu) * float(inv_produit_anterieur.prix_unit)
            #Les données du produits
            prix_un=float(inv_produit_anterieur.prix_unit)
            qte_un=quantite_vendu                 
         else:
               pass
      
      
      # VERIFICATION ET ENREGISTREMENT DE PRODUIT
      produits_valeur_vente=Valeurvente.query.filter_by(produitboutique_id=produit_vendu.id, facture_id=id_facture).first()
      montant_un= float(prix_un) *  float(qte_un)
      montant_deux= float(prix_deux) * float(qte_deux)
      montants=montant_un + montant_deux
      if produits_valeur_vente is None:
         valeur_vente_encours=Valeurvente(quantite=qte_un, quantite_s=qte_deux, prix_unitaire=prix_un, prix_unitaire_s=prix_deux, montant=montant_un,
                                          montant_s=montant_deux,montants=montants, produitboutique_id=produit_vendu.id, facture_id=id_facture)
         db.session.add(valeur_vente_encours)
         db.session.commit()
      else:
         produits_valeur_vente.quantite=produits_valeur_vente.quantite + qte_un
         produits_valeur_vente.quantite_s=produits_valeur_vente.quantite_s + qte_deux
         produits_valeur_vente.montant= float(produits_valeur_vente.montant) +float(montant_un) 
         produits_valeur_vente.montant_s=float(produits_valeur_vente.montant_s) + float(montant_deux)
         produits_valeur_vente.montants=float(produits_valeur_vente.montants) + float(montants)
         db.session.commit()

      #OPERATION DE STOCKAGE 
      stock_disponible_boutique=stockage_produit.disponible - quantite_vendu
      prix_unitaire_stock=float(stockage_produit.valeur_dispo)/float(stockage_produit.disponible)
      valeur_de_produit_sock=prix_unitaire_stock*stock_disponible_boutique
      #ENREGISTREMENT DE LA VENTE ET MODIFICATION DU STOCKAGE

     #Vérification de la vente du produit sur la facture
      vente_facture=Vente.query.filter_by(facture_id=id_facture,produitboutique_id=produit_vendu.id).first()
      if vente_facture is None:
         #Enregistrement de la vente
         print('-------------------Vente1------------------------------')
         vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
         db.session.add(vente_sur_facture)
      else:
         print('-------------------Vente2------------------------------')
         if prix_op_vente==vente_facture.prix_unitaire:
            print('-------------------Vente3------------------------------')
            mm_facture_qte=float(vente_facture.quantite) + float(quantite_vendu)
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 1', mm_facture_qte)

            mm_facture_valeur=float(vente_facture.montant) + float(valeur_de_produit)
            print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee 2', mm_facture_valeur)
            #Nouveau prix et nouvelle quantité
            vente_facture.quantite=mm_facture_qte
            vente_facture.montant=mm_facture_valeur
            
         else:
            print('-------------------Vente4------------------------------')
            vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
            db.session.add(vente_sur_facture)

      # Mise à jour du stock
      stockage_produit.solde=False
      stockage_boutique=Stock(quantite=quantite_vendu, valeur=valeur_de_produit, datest=date_facture, prix_unit=prix_op_vente, 
                           disponible=stock_disponible_boutique, 
                           valeur_dispo=valeur_de_produit_sock, vente_boutique=True, boutique_id=current_user.boutique_id, 
                           stock_user=current_user, produitboutique_id=produit_vendu.id, solde=True)
      db.session.add(stockage_boutique)

      # MISE A JOUR DE LA FACTURE
      mise_jr_facture=Facture.query.filter_by(id=id_facture).first()
      if mise_jr_facture.montant is None:
         mise_jr_facture.montant=valeur_de_produit
         mise_jr_facture.valeur_vendue=valeur_vendue_marchandise
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant ) + valeur_de_produit
         mise_jr_facture.valeur_vendue=float(mise_jr_facture.valeur_vendue) + float(valeur_vendue_marchandise)
      #Enregistrement et mise à des opération
      db.session.commit()
      if produit_vendu.emballage == 'Carton' or produit_vendu.emballage == 'Box':
         if quantite_par_produit== 0 or quantite_par_produit== 1:
            nbr_quantite_notification=(quantite_vendu/1)
            flash('Vous avez ajouté  {} {} de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
            return redirect(url_for('vente.grosinfofacture'))
         else:
            if produit_vendu.emballage == 'Carton':
               nbr_quantite_notification=round(quantite_vendu/quantite_par_produit,2)
               flash('Vous avez ajouté  {} {} de {}s '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               nbr_quantite_notification=round(quantite_vendu/quantite_par_produit,2)
               flash('Vous avez ajouté  {} {} de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
      else:
         if quantite_vendu > 1 :
            nbr_quantite_notification=quantite_vendu
            if produit_vendu.emballage == 'Vrac':
               flash('Vous avez ajouté  {} Pièces de {} '.format(nbr_quantite_notification,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               flash('Vous avez ajouté  {} {}s de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))

         else:
            if produit_vendu.emballage == 'Vrac':
               flash('Vous avez ajouté  {} Pièce de {} '.format(nbr_quantite_notification,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               flash('Vous avez ajouté  {} {} de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))

   # INJECTION DANS LE FORMULAIRE
   if request.method=='GET':
      x=0
      x=float(x)
      form.prix_vente_gros.data=x
   
   #LA FACTURE ENCOURS D'ETABLISSEMENT
   facture_encours_etablie=Vente.query.filter(Vente.facture_id==id_facture,Vente.no_facture==False, Vente.montant >=1  ).all()
   facture_donnes=Facture.query.filter_by(id=id_facture).first()
   ver_facture_encours="Vide"
   if facture_encours_etablie is not None:
      ver_facture_encours="NoVide"
   #DIMIUTION SUR LA FACTURE
   dimunition=DiminutionGFactureForm()

   return render_template('vente/vente_cash_detaille_gros.html',dimunition=dimunition,facture_d=facture_donnes,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, option_encours=option_encours, title=title, form=form, id_facture=id_facture)


""" Diminution de la facture gros"""
@vente.route('/dim/<int:facture>/<int:vente>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def gros_fact_dim(facture,vente):
   #FORMULAIRE DE DIMUTION
   dimunition=DiminutionGFactureForm()
   
   #NON ENVOIE DE PARAMETRE
   if facture is None or vente is None :
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.grosinfofacture'))

   #OPERATION DE DIMINUTION ENCOURS
   if dimunition.validate_on_submit():
      facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first()
      #Vérification de l'existence de la facture pour le client
      if facture_encours is None:
         flash("Attention cette opération est dangereuse","danger")
         return redirect(url_for('vente.grosinfofacture'))
      
      #LES VARIABLES PRINCIPALES
      quantite=None 
      nombre_de_quantite=dimunition.d_quantite.data
      #Vérification de la vente encours
      vente_encours=Vente.query.filter_by(id=vente,facture_id=facture, no_facture=False).first()

      # DETERMINATION DES QUANTITES EN GROS
      ratio_de_nomination=None
      quantite_par_produit=vente_encours.vente_produitboutique.nombre_contenu #Nombre de produit par emballage
      nomination_de_quantite=dimunition.nomination_d.data #Nomination de la quantité

      #Determination de ratio
      if nomination_de_quantite=='Quart':
         ratio_de_nomination=0.25
      elif nomination_de_quantite=='Demi':
         ratio_de_nomination=0.5
      else:
         ratio_de_nomination=1
      
      #Determination de la quantité
      if quantite_par_produit == 0 or quantite_par_produit == 1:
         quantite= 1 * nombre_de_quantite
      else:
         quantite=(quantite_par_produit * ratio_de_nomination) * nombre_de_quantite
         
      # VERIFICATIONS DES VENTES PRECEDENTES
      ver_vente_valeur=Valeurvente.query.filter_by(produitboutique_id=vente_encours.produitboutique_id, facture_id=facture).first()

      valeur_entree_sous=quantite * float(vente_encours.prix_unitaire)

      #DIMINUTION PROPREMENDITE
      if vente_encours.quantite >= quantite:
         #Valeurs en supression
         id_produit_encours=vente_encours.produitboutique_id
         ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_encours, boutique_id=current_user.boutique_id, solde=True).first()
         ver_stock.solde=False

          # Opération des ventes
         if ver_vente_valeur is not None:
            if ver_vente_valeur.quantite != 0 and ver_vente_valeur.quantite_s != 0:
               premiere_valeur = ver_vente_valeur.quantite - quantite
               if premiere_valeur < 0:
                  premier_valeur_correct= ver_vente_valeur.quantite
                  deuxieme_valeur_correct= quantite - ver_vente_valeur.quantite
                  #Valeur des ventes 
                  montant_pre=premier_valeur_correct * ver_vente_valeur.prix_unitaire
                  montant_de=deuxieme_valeur_correct * ver_vente_valeur.prix_unitaire_s
                  #Total montant
                  montant_total= montant_pre + montant_de
                  #Reste de la valeur de vente
                  reste_sur_vente= ver_vente_valeur.quantite_s - deuxieme_valeur_correct
                  valeur_reste= reste_sur_vente * ver_vente_valeur.prix_unitaire_s

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite = 0 
                  ver_vente_valeur.quantite_s = reste_sur_vente
                  ver_vente_valeur.montant = 0
                  ver_vente_valeur.montant_s = valeur_reste
                  ver_vente_valeur.prix_unitaire = 0
                  ver_vente_valeur.montants = valeur_reste

                  #Enregistrement de stock
                  disponible_un= ver_stock.disponible + premier_valeur_correct
                  valeur_dispo_un= float(ver_stock.valeur_dispo) + float(montant_pre) 

                  disponible_deux= disponible_un + deuxieme_valeur_correct
                  valeur_dispo_deux= valeur_dispo_un + float(montant_de)


                  stockage_boutique_un=Stock(quantite=premier_valeur_correct, valeur=montant_pre, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire, 
                                    disponible=disponible_un, 
                                    valeur_dispo=valeur_dispo_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours)

                  stockage_boutique_deux=Stock(quantite=deuxieme_valeur_correct, valeur=montant_de, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire_s, 
                                    disponible=disponible_deux, 
                                    valeur_dispo=valeur_dispo_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
                  db.session.add(stockage_boutique_un)
                  db.session.add(stockage_boutique_deux)

                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(montant_total)
               else:
                  premier_valeur_correct= ver_vente_valeur.quantite - quantite
                  qte_de_op=float(quantite)
                  #Valeur des ventes 
                  montant_pre=premier_valeur_correct * ver_vente_valeur.prix_unitaire
                  valeu_de_op=qte_de_op * float(ver_vente_valeur.prix_unitaire)

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite = premier_valeur_correct 
                  ver_vente_valeur.montant = montant_pre
                  ver_vente_valeur.montants = float(ver_vente_valeur.montants) - float(montant_pre)

                  #Enregistrement de stock
                  disponible_un= ver_stock.disponible + quantite
                  valeur_dispo_un= float(ver_stock.valeur_dispo) + float(valeu_de_op) 

                  stockage_boutique_un=Stock(quantite=qte_de_op, valeur=valeu_de_op, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire, 
                                    disponible=disponible_un, 
                                    valeur_dispo=valeur_dispo_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

                  db.session.add(stockage_boutique_un)
                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(valeu_de_op)
            elif ver_vente_valeur.quantite != 0 or ver_vente_valeur.quantite_s !=0:
               if ver_vente_valeur.quantite != 0 :
                  premier_valeur_correct= ver_vente_valeur.quantite - quantite
                  qte_de_op=float(quantite)
                  #Valeur des ventes 
                  montant_pre=premier_valeur_correct * ver_vente_valeur.prix_unitaire
                  valeu_de_op=qte_de_op * float(ver_vente_valeur.prix_unitaire)

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite = premier_valeur_correct 
                  ver_vente_valeur.montant = montant_pre
                  ver_vente_valeur.montants = float(ver_vente_valeur.montants) - float(montant_pre)

                  #Enregistrement de stock
                  disponible_un= ver_stock.disponible + quantite
                  valeur_dispo_un= float(ver_stock.valeur_dispo) + float(valeu_de_op) 

                  stockage_boutique_un=Stock(quantite=qte_de_op, valeur=valeu_de_op, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire, 
                                    disponible=disponible_un, 
                                    valeur_dispo=valeur_dispo_un, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

                  db.session.add(stockage_boutique_un)
                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(valeu_de_op)
               elif ver_vente_valeur.quantite_s != 0 :
                  deuxieme_valeur_correct= ver_vente_valeur.quantite_s - quantite
                  qte_de_op=float(quantite)
                  #Valeur des ventes 
                  montant_de=deuxieme_valeur_correct * ver_vente_valeur.prix_unitaire_s
                  valeu_de_op=qte_de_op * float(ver_vente_valeur.prix_unitaire_s)

                  #Mise à jour de la facture.
                  ver_vente_valeur.quantite_s = deuxieme_valeur_correct 
                  ver_vente_valeur.montant_s = montant_de
                  ver_vente_valeur.montants = float(ver_vente_valeur.montants) - float(montant_de)

                  #Enregistrement de stock
                  disponible_deux= ver_stock.disponible + quantite
                  valeur_dispo_deux= float(ver_stock.valeur_dispo) + float(valeu_de_op) 

                  stockage_boutique_deux=Stock(quantite=qte_de_op, valeur=valeu_de_op, datest=facture_encours.date, prix_unit=ver_vente_valeur.prix_unitaire_s, 
                                    disponible=disponible_deux, 
                                    valeur_dispo=valeur_dispo_deux, facture_annule=True, boutique_id=current_user.boutique_id, 
                                    stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)

                  db.session.add(stockage_boutique_deux)
                  #Mise à jour de la facture
                  facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - float(valeu_de_op)
             
         #SOUSTRACTION DES QUANTITES ET DES VALEURS
         quantite_vente_encours=vente_encours.quantite
         quantite_entree = quantite
         #Soustraction
         nouvelle_quantite=float(quantite_vente_encours) - quantite_entree
         nv=nouvelle_quantite * float(vente_encours.prix_unitaire)
         valeur=nv

         #Enregistrement de la diminution de la vente
         vente_encours.quantite=nouvelle_quantite
         vente_encours.montant=valeur

         #FACTURE ENCOURS
         nv_f=float(facture_encours.montant) - valeur_entree_sous
         #Soustraction
         facture_encours.montant=nv_f
         #COMMIT DES OPERATIONS
         db.session.commit()
         if vente_encours.vente_produitboutique.emballage == 'Carton' or vente_encours.vente_produitboutique.emballage == 'Box':
            if quantite_par_produit== 0 or quantite_par_produit== 1:
               nbr_quantite_notification=(quantite/1)
               flash('Vous avez retiré  {} {} de {} '.format(nbr_quantite_notification,vente_encours.vente_produitboutique.emballage,vente_encours.vente_produitboutique.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               if vente_encours.vente_produitboutique.emballage == 'Carton':
                  nbr_quantite_notification=round(quantite/quantite_par_produit,2)
                  flash('Vous avez retiré  {} {}s de {} '.format(nbr_quantite_notification,vente_encours.vente_produitboutique.emballage,vente_encours.vente_produitboutique.nom_produit),'success')
                  return redirect(url_for('vente.grosinfofacture'))
               else:
                  nbr_quantite_notification=round(quantite/quantite_par_produit,2)
                  flash('Vous avez retiré  {} {} de {} '.format(nbr_quantite_notification,vente_encours.vente_produitboutique.emballage,vente_encours.vente_produitboutique.nom_produit),'success')
                  return redirect(url_for('vente.grosinfofacture'))
         else:
            nbr_quantite_notification=quantite
            if quantite > 1 :
               
               flash('Vous avez retiré  {} {}s de {} '.format(nbr_quantite_notification,vente_encours.vente_produitboutique.emballage,vente_encours.vente_produitboutique.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
            else:
               flash('Vous avez retiré  {} {} de {} '.format(nbr_quantite_notification,vente_encours.vente_produitboutique.emballage,vente_encours.vente_produitboutique.nom_produit),'success')
               return redirect(url_for('vente.grosinfofacture'))
      else:
         flash("Vérifier la quantité de ce produit sur la facture","danger")
         return redirect(url_for('vente.grosinfofacture'))


""" Suppression sur la facture"""
@vente.route('/gros/sup-<int:facture>/<int:vente>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def gros_fact_sup(facture,vente):
    
   #NON ENVOIE DE PARAMETRE
   if facture is None and vente is None :
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.grosinfofacture'))

   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first()
   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.grosinfofacture'))
   
   #Vérification de la vente encours
   vente_encours=Vente.query.filter_by(id=vente,facture_id=facture).first()

   #Quantité à diminuer dans la facture
   quantite=vente_encours.quantite

   #DIMINUTION PROPREMENDITE

   quantite_vente_encours=vente_encours.quantite
   quantite_entree = quantite
   #Soustraction
   nouvelle_quantite=quantite_vente_encours - quantite_entree
   nv=quantite* vente_encours.prix_unitaire
   valeur=nv
   #Enregistrement de la diminution de la vente
   vente_encours.quantite=nouvelle_quantite
   vente_encours.montant=valeur
   vente_encours.no_facture=True

   #FACTURE ENCOURS
   nv_f=facture_encours.montant - valeur
   #Soustraction
   facture_encours.montant=nv_f

   #SOCK DISPONIBLE
   id_produit_encours=vente_encours.produitboutique_id
   ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_encours, boutique_id=current_user.boutique_id, solde=True).first()
   ver_stock.solde=False
   #Les variable de stockage
   qte_stock_encours=ver_stock.disponible + quantite
   quantite_valeur_op=quantite*vente_encours.prix_unitaire # La valeur de l'opération
   valeurs_nouvelle_dispo= ver_stock.valeur_dispo + quantite_valeur_op

   #ENREGSITREMENT DU SOCKAGE
   stockage_boutique=Stock(quantite=quantite, valeur=quantite_valeur_op, datest=facture_encours.date, prix_unit=vente_encours.prix_unitaire, 
                     disponible=qte_stock_encours, 
                     valeur_dispo=valeurs_nouvelle_dispo, facture_annule=True, boutique_id=current_user.boutique_id, 
                     stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
   db.session.add(stockage_boutique)
   db.session.commit()
   flash("Vous avez supprimé le {} sur la facture".format(vente_encours.vente_produitboutique.nom_produit),"success")
   return redirect(url_for('vente.grosinfofacture'))


#-------------------------------------------------------------- VENTE EN DETTE -----------------------------------------------------

""" Liste des factures en dette"""
@vente.route('/dette', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def dette():  
   #Liste des factures
   option_encours='vente'
   title='Les factures'
   form=RechercheDFactureForm()
   page= request.args.get('page', 1, type=int)
   list_facture=None
   list_facture=Facture.query.filter(Facture.dette==True, Facture.annule==False).order_by(Facture.id.desc()).paginate(page=page, per_page=50)
   ver_facture_sub="Vide"
   liste_donne=None

   #Session de supression de la facture sur la plateforme
   session['annuler_facture']=False

   if form.validate_on_submit():
      code_id_facture=form.facture_client.data.id
      liste_donne=Facture.query.filter_by(id=code_id_facture).first()
      ver_facture_sub="NoVide" 
   return render_template('vente/dette.html',form=form, liste=liste_donne, title=title, ver_facture_sub=ver_facture_sub, listes=list_facture, option_encours=option_encours)


""" Payement de la facture"""
@vente.route('/payement_facture/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def payement_facture(facture):
   option_encours='vente'
   title='Vente'
   
   
   #Initialisation de la variable encours
   id_facture=None
   if facture is None:
      return redirect(url_for('vente.dette'))
   else:
      id_facture=facture

   #Formulaire de la facture
   form=PayementFactureForm()
   # La date
   aujourd=date.today()
   #Code de la facture
   code_fact_one=utilitaire.codefacture() #Code facture

   #Payement par compte
   rech=RechercheForm()

   nouveau_code_facture=None
   code_facture=Facture.query.filter_by(liquidation=True).order_by(Facture.id.desc()).first()
   if code_facture is None:
      nouveau_code_facture="PD-{}1".format(code_fact_one)
   else:
      nouveau_code_facture="PD-{}{}".format(code_fact_one, code_facture.id)


   #ENREGISTREMENT DE LA VENTE SUR LA FACTURE
   if form.validate_on_submit():

      facture_dimunition=Facture.query.filter_by(id=id_facture).first()
      #Le montant de la facture
      montant_global=float(facture_dimunition.montant)
      montant_payer=float(form.payement_facture.data)
      #Verification du montant payé par rapport au montant du
      if montant_payer > montant_global:
         flash('Le montant payé est supieur au montant du de ${}'.format(round(montant_global,2)),"danger")
      if montant_global == 0:
         flash("La facture est liquidée déjà","danger")
         return redirect(url_for('vente.payement_facture',facture=facture))

      message_dela_facture=" Payement de la facture {}".format(facture_dimunition.code_facture)
      #Payement de la facture
      montant_global_payement=montant_global- montant_payer
      val_vendue_stock=None

      if montant_global_payement== 0:
         paiement_facture=Payement(code_payement=nouveau_code_facture,montant=montant_payer,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
         facture_dimunition.valeur_vendue=0
         val_vendue_stock=0


      else:
         pourcentage_de_payement=(montant_payer/montant_global)
         montant_equivalent= pourcentage_de_payement * float(facture_dimunition.valeur_vendue)
         val_vendue_stock=montant_equivalent
         #Reste de la facture
         reste_fact=float(facture_dimunition.valeur_vendue)-montant_equivalent
         paiement_facture=Payement(code_payement=nouveau_code_facture,liquidation=True, montant=montant_payer,denomination=message_dela_facture,date=aujourd,facture_id=facture_dimunition.id)
         facture_dimunition.valeur_vendue=reste_fact

      db.session.add(paiement_facture)
      # Dimunition de la facture
      facture_dimunition.liquidation=True
      facture_dimunition.montant=montant_global_payement
      operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id,liquidation=True, montant=montant_payer, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente, valeur_vendue=val_vendue_stock)
      db.session.add(operation_facture)
      db.session.commit()
      flash("Vous avez payé ${}".format(round(montant_payer,2)),"success")
      return redirect(url_for('vente.dette'))

   #LA FACTURE ENCOURS D'ETABLISSEMENT
   facture_encours_etablie=Vente.query.filter_by(facture_id=id_facture,no_facture=False).all()
   facture_donnes=Facture.query.filter_by(id=id_facture).first()
   payement_facture_etablie=Payement.query.filter_by(facture_id=id_facture).all()

   ver_facture_encours="Vide"
   if facture_encours_etablie is not None:
      ver_facture_encours="NoVide"
   
   nombre_total_payer=[]
   nbr_tot_payer=None
   for i in payement_facture_etablie:
      a=i.montant
      nombre_total_payer.insert(0,a)
   nbr_tot_payer=sum(nombre_total_payer)

   nombre_total_dette=[]
   nbr_tot_dette=None
   for fac in facture_encours_etablie:
      a=fac.montant
      nombre_total_dette.insert(0,a)
   nbr_tot_dette=sum(nombre_total_dette)


   
   return render_template('vente/payementdette.html', rech=rech, nbr_tot_dette=nbr_tot_dette, nbr_tot_payer=nbr_tot_payer, payements=payement_facture_etablie,facture_d=facture_donnes,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, option_encours=option_encours, title=title, form=form)


""" Payement de la facture"""
@vente.route('/payement_facture_total/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def payement_facture_total(facture):
   option_encours='vente'
   title='Vente'
   #Initialisation de la variable encours
   id_facture=None
   if facture is None:
      return redirect(url_for('vente.dette'))
   else:
      id_facture=facture

   # La date
   aujourd=date.today()
   #Code de la facture
   code_fact_one=utilitaire.codefacture() #Vérfication code de la facture

   nouveau_code_facture=None
   code_facture=Facture.query.filter_by(liquidation=True).order_by(Facture.id.desc()).first()
   if code_facture is None:
      nouveau_code_facture="PD-{}1".format(code_fact_one)
   else:
      nouveau_code_facture="PD-{}{}".format(code_fact_one, code_facture.id)

   facture_dimunition=Facture.query.filter_by(id=id_facture).first_or_404()
   #Le montant de la facture
   montant_global=float(facture_dimunition.montant)
   montant_payer=float(facture_dimunition.montant)
   #Verification du montant payé par rapport au montant du
   if montant_payer > montant_global:
      flash('Le montant payé est supieur au montant du de ${}'.format(round(montant_global,2)),"danger")
   if montant_global == 0:
      flash("La facture est liquidée déjà","danger")
      return redirect(url_for('vente.payement_facture',facture=facture))

      
   message_dela_facture=" Payement de la facture {}".format(facture_dimunition.code_facture)
   #Payement de la facture
   montant_global_payement=montant_global- montant_payer
   val_vente_stock=facture_dimunition.valeur_vendue
   if montant_global_payement== 0:
      paiement_facture=Payement(code_payement=nouveau_code_facture,montant=montant_payer,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
   else:
      paiement_facture=Payement(code_payement=nouveau_code_facture,liquidation=True, montant=montant_payer,denomination=message_dela_facture,date=aujourd,facture_id=facture_dimunition.id)
   db.session.add(paiement_facture)
   # Dimunition de la facture
   facture_dimunition.liquidation=True
   facture_dimunition.montant=montant_global_payement
   facture_dimunition.valeur_vendue=0
   operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id, liquidation=True, montant=montant_payer, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente, valeur_vendue=val_vente_stock)
   db.session.add(operation_facture)
   db.session.commit()
   flash("Vous avez payé ${}".format(round(montant_payer,2)),"success")
   return redirect(url_for('vente.dette'))


""" Payement de la facture"""
@vente.route('/compte/payement_facture_total/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def payement_facture_total_compte(facture):
   option_encours='vente'
   title='Vente'
   #Initialisation de la variable encours
   id_facture=None
   if facture is None:
      return redirect(url_for('vente.dette'))
   else:
      id_facture=facture

   # La date
   aujourd=date.today()
   #Code de la facture
   code_fact_one=utilitaire.codefacture() #Vérfication code de la facture

   rech=RechercheForm()

   if rech.validate_on_submit():
      data_compte=rech.clients_client.data

      nouveau_code_facture=None
      code_facture=Facture.query.filter_by(liquidation=True).order_by(Facture.id.desc()).first()
      if code_facture is None:
         nouveau_code_facture="PD-{}1".format(code_fact_one)
      else:
         nouveau_code_facture="PD-{}{}".format(code_fact_one, code_facture.id)

      facture_dimunition=Facture.query.filter_by(id=id_facture).first_or_404()
      #Les données de dimunition
      valeur_diminution=facture_dimunition.valeur_vendue
      #Le montant de la facture
      montant_global=float(facture_dimunition.montant)
      #Solde du compte du client 
      if data_compte.solde is None or data_compte.solde == 0:
            flash("Impossible d'effectuer cette opération le compte client est égal à Zéro","danger")
            return redirect(url_for('vente.payement_facture', facture=facture))

      solde_client_compte=float(data_compte.solde)
      message_dela_facture=" Payement de la facture {} par compte client".format(facture_dimunition.code_facture)

      if solde_client_compte >= montant_global:
         #Payement de la facture encours
         montant_global_payement = solde_client_compte - montant_global
         paiement_facture=Payement(code_payement=nouveau_code_facture,montant=montant_global,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
         facture_dimunition.liquidation=True
         facture_dimunition.montant=0
         operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id, liquidation=True, montant=montant_global, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente, valeur_vendue=valeur_diminution)
         db.session.add(operation_facture)
         #Retrait sur le compte de l'opération
         motif=f"Payement de la facture de dette {facture_dimunition.code_facture} "
         insert_operation=Operation(motif=motif, montant=montant_global, type_transanction='Retrait',
                                    compte_id=data_compte.id, date=aujourd)
         db.session.add(insert_operation)
         #Mise à du solde du compte
         data_compte.solde=montant_global_payement

         db.session.commit()
         flash("Vous avez payé ${}".format(round(montant_global,2)),"success")
         
         return redirect(url_for('vente.dette'))
      else:
         if solde_client_compte == 0:
            flash("Impossible d'effectuer cette opération le compte client est égal à Zéro","danger")
            return redirect(url_for('vente.payement_facture', facture=facture))
         elif solde_client_compte is None:
            flash("Impossible d'effectuer cette opération le compte client est égal à Zéro","danger")
            return redirect(url_for('vente.payement_facture', facture=facture))
         elif  solde_client_compte > 0:
            montant_global_payement = montant_global  -  solde_client_compte
            #Les opérations d'equivalence de la facture
            pourcentage_de_payement=(solde_client_compte/montant_global)
            montant_equivalent= pourcentage_de_payement * float(facture_dimunition.valeur_vendue)
            val_vendue_stock=montant_equivalent
            #Reste de la facture
            reste_fact=float(facture_dimunition.valeur_vendue)-montant_equivalent

            paiement_facture=Payement(code_payement=nouveau_code_facture,montant=solde_client_compte,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
            facture_dimunition.liquidation=True
            facture_dimunition.montant= montant_global_payement
            facture_dimunition.valeur_vendue=reste_fact
            operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id, liquidation=True, montant=solde_client_compte, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente, valeur_vendue=val_vendue_stock)
            db.session.add(operation_facture)
            #Retrait sur le compte de l'opération
            motif=f"Payement de la facture de dette {facture_dimunition.code_facture} "

            insert_operation=Operation(motif=motif, montant=solde_client_compte, type_transanction='Retrait',
                                       compte_id=data_compte.id, date=aujourd)
            db.session.add(insert_operation)
            #Mise à du solde du compte
            data_compte.solde=0
            db.session.commit()
            flash("Vous avez payé ${}".format(round(montant_global,2)),"success")
            
            return redirect(url_for('vente.dette'))

#--------------------------------------- VENTE ACOMPTE -------------------------------------------------------------

""" Les informations de la facture acompte cash"""
@vente.route('/acompte/infos_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def infofactureacompte():
   option_encours='vente'
   title='Vente'
   
   #FACTURE ETABLIE 
   id_facture=utilitaire.id_facture_client()
   date_facture=utilitaire.facture_date()

   if id_facture is None:
      #return redirect(url_for('vente.acompte'))
      pass

   #Formulaire de la facture
   form=VenteFactureForm()

   #ENREGISTREMENT DE LA VENTE SUR LA FACTURE
   if form.validate_on_submit():
      #LES VARIABLES PRINCIPALES
      prix_du_produit=form.prix_vente_detaille.data #Prix du produit
      quantite_vendu=form.quantite.data #Quantité
      produit_vendu =form.produit_vente.data # Produit vendu

      #OPERATION DE LA VENTE SUR LES VARIABLES

      #Prix de l'operation
      prix_op_vente=None
      if prix_du_produit==0:
         if produit_vendu.emballage == "Carton" or produit_vendu.emballage == "Box": 
            nbr_cont_pro=None
            if produit_vendu.nombre_contenu==0:
               nbr_cont_pro=1
            else:
               nbr_cont_pro=produit_vendu.nombre_contenu
            prix_op_vente=float(produit_vendu.vt_detaille_piece)   # Prix en fonction de produit
         else:
            prix_op_vente=produit_vendu.vt_detaille_piece
      else:
         prix_op_vente=prix_du_produit #Prix en fonction de la variation
      #Valeur de la transanction
      valeur_de_produit=float(prix_op_vente*quantite_vendu)
      #Données de la valeur de vente
      ver_valeur_produit_stock=Valeurvente.query.filter_by(facture_id=id_facture,produitboutique_id=produit_vendu.id).first()

      # MISE A JOUR DE LA FACTURE
      mise_jr_facture=Facture.query.filter_by(id=id_facture).first()

      quantite_op_encours=quantite_vendu
      prix_de_vente=None
      montants=None
      if ver_valeur_produit_stock is None:
         stock_verification=Stock.query.filter_by(produitboutique_id=produit_vendu.id, stockage=True, boutique_id=current_user.boutique_id).order_by(Stock.id.desc()).first()
         prix_de_vente=stock_verification.prix_unit

         montants=float(prix_de_vente) * float(quantite_op_encours)
         enregistrement_op=Valeurvente(quantite=0, prix_unitaire=0, montant=0, quantite_s=quantite_op_encours, prix_unitaire_s=prix_de_vente, montant_s=montants, montants=montants, facture_id=id_facture,produitboutique_id=produit_vendu.id)
         db.session.add(enregistrement_op)
         # Mise à jour de la valeur de vente
         mise_jr_facture.valeur_vendue=montants

      else:
         stock_verification=Stock.query.filter_by(produitboutique_id=produit_vendu.id, stockage=True, boutique_id=current_user.boutique_id).order_by(Stock.id.desc()).first()
         prix_de_vente=stock_verification.prix_unit
         montants=float(prix_de_vente) * float(quantite_op_encours)
         #Valeur de facture des données
         ver_valeur_produit_stock.quantite_s=int(ver_valeur_produit_stock.quantite_s) + int(quantite_op_encours)
         ver_valeur_produit_stock.montant_s=float(ver_valeur_produit_stock.montant_s) + montants
         ver_valeur_produit_stock.montants=float(ver_valeur_produit_stock.montants) + montants

         mise_jr_facture.valeur_vendue=float(mise_jr_facture.valeur_vendue) +  montants


      #ENREGISTREMENT DE LA VENTE ET MODIFICATION DU STOCKAGE
      #Vérification de la vente du produit sur la facture
      vente_facture=Vente.query.filter_by(facture_id=id_facture,produitboutique_id=produit_vendu.id).first()
      if vente_facture is None:
         #Enregistrement de la vente
         vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
         db.session.add(vente_sur_facture)
      else:
         if prix_op_vente==vente_facture.prix_unitaire:
            mm_facture_qte=vente_facture.quantite + quantite_vendu
            mm_facture_valeur=float(vente_facture.montant) + valeur_de_produit
            #Nouveau prix et nouvelle quantité
            vente_facture.quantite=mm_facture_qte
            vente_facture.montant=mm_facture_valeur
         else:
            vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
            db.session.add(vente_sur_facture)


      
      if mise_jr_facture.montant is None:
         mise_jr_facture.montant=valeur_de_produit
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant ) + valeur_de_produit
      
      #DEPOT DE L'ARGENT DANS LE COMPTE
      client_compte=None
      solde_compte=None
      if 'client_compte' in session:
         client_compte=session['client_compte']
      
      operations_compte=Operation.query.filter_by(facture=id_facture, compte_id=client_compte).first()
      comptes_en_modification=Comptes.query.filter_by(id=client_compte).first()

      motif=f" Acompte sur la facture {mise_jr_facture.code_facture} "
      if operations_compte is None:
         insert_operation=Operation(motif=motif, montant=valeur_de_produit, type_transanction='Dépôt',
                                    compte_id=client_compte, date=mise_jr_facture.date, facture=id_facture)
         db.session.add(insert_operation)
      else:
         operations_compte.montant=float(operations_compte.montant) + valeur_de_produit

      if comptes_en_modification.solde is None:
         solde_compte=0
      else:
         solde_compte=float(comptes_en_modification.solde)

      comptes_en_modification.solde= solde_compte + valeur_de_produit
     
      #Enregistrement et mise à des opération
      db.session.commit()
      embal=utilitaire.emballage_taille_accompte(quantite_vendu)
      flash('Vous avez ajouté {} et de {} {} '.format(produit_vendu.nom_produit, quantite_vendu,embal),'success')
      return redirect(url_for('vente.infofactureacompte'))

   # INJECTION DANS LE FORMULAIRE
   if request.method=='GET':
      x=0
      x=float(x)
      form.prix_vente_detaille.data=x
   
   #LA FACTURE ENCOURS D'ETABLISSEMENT
   facture_encours_etablie=Vente.query.filter_by(facture_id=id_facture,no_facture=False).all()
   facture_donnes=Facture.query.filter_by(id=id_facture).first()
   ver_facture_encours="Vide"
   if facture_encours_etablie is not None:
      ver_facture_encours="NoVide"
   
   #DIMIUTION SUR LA FACTURE
   dimunition=DiminutionFactureForm()

   return render_template('vente/vente_cash_detaille_acompte.html',dimunition=dimunition,facture_d=facture_donnes,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, option_encours=option_encours, title=title, form=form, id_facture=id_facture)


""" Diminution de la facture cash accompte"""
@vente.route('/acompte/dim-<int:facture>/<int:vente>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def fact_dim_acompte(facture,vente):
   #FORMULAIRE DE DIMUTION
   dimunition=DiminutionFactureForm()
   
   #NON ENVOIE DE PARAMETRE
   if facture is None and vente is None :
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.infofactureacompte'))

   #OPERATION DE DIMINUTION ENCOURS
   if dimunition.validate_on_submit():
      facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first()

      #Vérification de l'existence de la facture pour le client
      if facture_encours is None:
         flash("Attention cette opération est dangereuse","danger")
         return redirect(url_for('vente.infofactureacompte'))

      #Quantité à diminuer dans la facture
      quantite=dimunition.d_quantite.data
      #Vérification de la vente encours
      vente_encours=Vente.query.filter_by(id=vente,facture_id=facture).first()

      valeur_entree_sous=quantite * float(vente_encours.prix_unitaire)
        
      #DIMINUTION PROPREMENDITE
      if vente_encours.quantite >=quantite:
         quantite_vente_encours=vente_encours.quantite
         quantite_entree = quantite
         #Soustraction
         nouvelle_quantite=quantite_vente_encours - quantite_entree
         nv=float(nouvelle_quantite) * float(vente_encours.prix_unitaire)
         valeur=nv
         #Enregistrement de la diminution de la vente
         vente_encours.quantite=nouvelle_quantite
         vente_encours.montant=valeur

         #FACTURE ENCOURS
         nv_f=float(facture_encours.montant) - valeur_entree_sous
         #Soustraction
         facture_encours.montant=nv_f
         #Facture 
         db.session.commit()

         id_produit_op=vente_encours.produitboutique_id
         id_facture_op=vente_encours.facture_id


         quantite_op_encours=quantite
         prix_de_vente=None
         montants=None

         verification_produit=Valeurvente.query.filter_by(produitboutique_id=id_produit_op, facture_id=id_facture_op).first()
         if verification_produit is not None:
            prix_de_vente=verification_produit.prix_unitaire_s
            montants= float(prix_de_vente) * quantite_op_encours
            # Valeur de produit
            verification_produit.quantite_s=int(verification_produit.quantite_s) - int(quantite_op_encours)
            verification_produit.montant_s=float(verification_produit.montant_s) - montants
            verification_produit.montants=float(verification_produit.montants) - montants

            facture_encours.valeur_vendue= float(facture_encours.valeur_vendue) - montants
            # COMMIT
            db.session.commit()

         flash("Vous avez diminuer une quantité de {}".format(quantite),"success")
         return redirect(url_for('vente.infofactureacompte'))
      else:
         flash("Vous avez une quantité de {}".format(vente_encours.quantite),"danger")
         return redirect(url_for('vente.infofactureacompte'))
   return render_template('vente/facture.html')


""" Liste des factures acompte"""
@vente.route('/acompte', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def acompte():  
   #Liste des factures
   option_encours='vente'
   title='Les factures'
   form=RechercheAFactureForm()
   page= request.args.get('page', 1, type=int)
   list_facture=None
   #Suppression de session
   session.pop('idfacture', None)
   session.pop('datefacture', None)
   session.pop('validation', None)
   session.pop('validation_dette', None)
   session.pop('validation_acompte', None)

   #Session de supression de la facture sur la plateforme
   session['annuler_facture_acompte']=True

   list_facture=Facture.query.filter(Facture.vente_acompte==True, Facture.montant >=1, Facture.annule==False).order_by(Facture.id.desc()).paginate(page=page, per_page=50)
   ver_facture_sub="Vide"
   liste_donne=None
   if form.validate_on_submit():
      code_id_facture=form.facture_client.data.id
      liste_donne=Facture.query.filter_by(id=code_id_facture).first()
      ver_facture_sub="NoVide" 
   return render_template('vente/acompte.html',form=form, liste=liste_donne, title=title, ver_facture_sub=ver_facture_sub, listes=list_facture, option_encours=option_encours)

""" Regler la facture"""
@vente.route('/acompte/facture/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def acompte_facture(facture):
    
   #NON ENVOIE DE PARAMETRE
   if facture is None:
      abort(404)
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.acompte'))

   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first_or_404()
   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.acompte'))
   
   #Vérification de la vente encours
   vente_encours=Vente.query.filter_by(facture_id=facture).all()

   le_stock_insuffisant=[]

   aujourd=date.today()
   #ANNULATION DE LA FACTURE
   for an_fact in vente_encours:
      stockage_produit=Stock.query.filter_by(produitboutique_id=an_fact.vente_produitboutique.id, boutique_id=current_user.boutique_id, solde=True).first()
      if stockage_produit is not None:
         if stockage_produit.disponible < an_fact.quantite:
            pro_acompte=an_fact.vente_produitboutique.nom_produit
            le_stock_insuffisant.insert(0,pro_acompte)
         elif stockage_produit.disponible >= an_fact.quantite :
            valeur= float(an_fact.prix_unitaire) * float(an_fact.quantite)
            disponible_stock=stockage_produit.disponible - an_fact.quantite
            valeur_dispo_acompte= float(stockage_produit.valeur_dispo) - valeur
            stockage_produit.solde=False
            stockage_boutique=Stock(quantite=an_fact.quantite, valeur=valeur, datest=aujourd, prix_unit=an_fact.prix_unitaire, 
                           disponible=disponible_stock, valeur_dispo=valeur_dispo_acompte, vente_boutique=True, boutique_id=current_user.boutique_id, 
                           stock_user=current_user, produitboutique_id=an_fact.vente_produitboutique.id, solde=True)
            db.session.add(stockage_boutique)
            facture_encours.valide_account=True
            db.session.commit()
            flash(f"La facture d'acompte {facture_encours.code_facture} est apurement ", "success")
            return redirect(url_for('vente.acompte'))
            
      else:
         flash("Un ou plusieurs produits ne sont pas dans votre stock ", "danger")
         return redirect(url_for('vente.acompte'))
      
   nombre_de_produit=len(le_stock_insuffisant)
   if nombre_de_produit > 0:
      if nombre_de_produit==1:
         flash(f"Le stock de c'est porduit {le_stock_insuffisant[0]} est  inférieur au stock de l'acompte  ", "danger")
      else:
         flash(f"Le stock de ces produits {str(le_stock_insuffisant) } sont inférieur au stock de l'acompte ", "danger")
      return redirect(url_for('vente.acompte'))


""" SUpprimer la facture de l'acompte """
@vente.route('/acompte/facture/sup/<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def sup_acompte_facture(facture):
    
   #NON ENVOIE DE PARAMETRE
   if facture is None:
      abort(404)
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.acompte'))

   #VERIFICATION DE LA FACTURE
   facture_encours=Facture.query.filter_by(id=facture, facture_user=current_user).first_or_404()
   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.acompte'))
   
   #Vérification de la vente encours
   vente_encours=Vente.query.filter_by(facture_id=facture).all()
   #Suppresion des valeurs de vente
   vente_valeurs_encours=Valeurvente.query.filter_by(facture_id=facture).all()
   if vente_valeurs_encours != []:
      for val in vente_valeurs_encours:
         Valeurvente.query.filter_by(id=val.id).delete()
         db.session.commit()

   

   le_stock_insuffisant=[]

   aujourd=date.today()
   #ANNULATION DE LA FACTURE
   for an_fact in vente_encours:
      stockage_produit=Stock.query.filter_by(produitboutique_id=an_fact.vente_produitboutique.id, boutique_id=current_user.boutique_id, solde=True).first()
      
      if facture_encours.valide_account==True:
      #Le produit 
         vente_va_don=Valeurvente.query.filter_by(produitboutique_id=an_fact.vente_produitboutique.id, facture_id=facture).first()

         valeur= float(vente_va_don.prix_unitaire_s) * float(vente_va_don.quantite_s)
         disponible_stock=stockage_produit.disponible + vente_va_don.quantite_s
         valeur_dispo_acompte= float(stockage_produit.valeur_dispo) + valeur
         stockage_produit.solde=False
         stockage_boutique=Stock(quantite=vente_va_don.quantite_s, valeur=valeur, datest=aujourd, prix_unit=vente_va_don.prix_unitaire_s, 
                        disponible=disponible_stock, valeur_dispo=valeur_dispo_acompte, vente_boutique=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=an_fact.vente_produitboutique.id, solde=True)
         db.session.add(stockage_boutique)
         Vente.query.filter_by(id=an_fact.id).delete()
         db.session.commit()
      else:
         Vente.query.filter_by(id=an_fact.id).delete()
         db.session.commit()
   
   vente_valeurs_encours=Valeurvente.query.filter_by(facture_id=facture).all()
   if vente_valeurs_encours != []:
      for val in vente_valeurs_encours:
         Valeurvente.query.filter_by(id=val.id).delete()
         db.session.commit()

   Facture.query.filter_by(id=facture).delete()
   db.session.commit()
   flash("Votre facture a été suprimer","success")
   return redirect(url_for('vente.acompte'))
      
 
""" Les informations de la facture en gros"""
@vente.route('/acompte/gros_infos_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def grosinfofactureacompte():
   option_encours='vente'
   title='Vente'
   
   #FACTURE ETABLIE 
   id_facture=utilitaire.id_facture_client()
   date_facture=utilitaire.facture_date()

   if id_facture is None:
      return redirect(url_for('vente.facturecash'))

   #Formulaire de la facture
   form=VenteFactureGForm()

   #ENREGISTREMENT DE LA VENTE SUR LA FACTURE
   if form.validate_on_submit():
      #LES VARIABLES PRINCIPALES
      prix_du_produit=form.prix_vente_gros.data #Prix du produit
      produit_vendu =form.produit_vente.data # Produit vendu
      nombre_de_quantite=form.quantite.data
      # DETERMINATION DES QUANTITES EN GROS
      quantite_vendu=None 
      ratio_de_nomination=None
      quantite_par_produit=produit_vendu.nombre_contenu #Nombre de produit par emballage
      nomination_de_quantite=form.nomination.data #Nomination de la quantité
      #Determination de ratio
      if nomination_de_quantite=='Quart':
         ratio_de_nomination=0.25
      elif nomination_de_quantite=='Demi':
         ratio_de_nomination=0.5
      else:
         ratio_de_nomination=1
      
      #Determination de la quantité
      if quantite_par_produit== 0 or quantite_par_produit== 1:
         quantite_vendu= 1 * nombre_de_quantite
      else:
         quantite_vendu=(quantite_par_produit * ratio_de_nomination) * nombre_de_quantite
         
      #OPERATION DE LA VENTE SUR LES VARIABLES
      #Prix de l'operation
      prix_op_vente=None

      if prix_du_produit==0:
         if produit_vendu.emballage == "Carton" or produit_vendu.emballage == "Box": 
            nbr_cont_pro=None
            if produit_vendu.nombre_contenu==0:
               nbr_cont_pro=1
            else:
               nbr_cont_pro=produit_vendu.nombre_contenu
            prix_op_vente=float(produit_vendu.vt_gros_entier/nbr_cont_pro)   # Prix en fonction de produit
         else:
            prix_op_vente=produit_vendu.vt_gros_entier 
      else:
         prix_op_vente=prix_du_produit #Prix en fonction de la variation
      #Valeur de la transanction
      valeur_de_produit=float(prix_op_vente*quantite_vendu)

      #ENREGISTREMENT DE LA VENTE ET MODIFICATION DU STOCKAGE
      
      #Vérification de la vente du produit sur la facture
      vente_facture=Vente.query.filter_by(facture_id=id_facture,produitboutique_id=produit_vendu.id, no_facture=False).first()
      if vente_facture is None:
         #Enregistrement de la vente
         vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
         db.session.add(vente_sur_facture)
      else:
         if prix_op_vente==vente_facture.prix_unitaire:
            mm_facture_qte=float(vente_facture.quantite) + quantite_vendu
            mm_facture_valeur=float(vente_facture.montant) + valeur_de_produit
            #Nouveau prix et nouvelle quantité
            vente_facture.quantite=mm_facture_qte
            vente_facture.montant=mm_facture_valeur
         else:
            vente_sur_facture=Vente(quantite=quantite_vendu, montant=valeur_de_produit, prix_unitaire=prix_op_vente, no_facture=0, facture_id=id_facture,produitboutique_id=produit_vendu.id)
            db.session.add(vente_sur_facture)

      # MISE A JOUR DE LA FACTURE
      mise_jr_facture=Facture.query.filter_by(id=id_facture).first()
      if mise_jr_facture.montant is None:
         mise_jr_facture.montant=valeur_de_produit
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant) + valeur_de_produit
      
      #DEPOT DE L'AGGENT DANS LE COMPTE
      client_compte=None
      solde_compte=None
      if 'client_compte' in session:
         client_compte=session['client_compte']
      
      operations_compte=Operation.query.filter_by(facture=id_facture, compte_id=client_compte).first()
      comptes_en_modification=Comptes.query.filter_by(id=client_compte).first()

      motif=f" Acompte sur la facture {mise_jr_facture.code_facture} "
      if operations_compte is None:
         insert_operation=Operation(motif=motif, montant=valeur_de_produit, type_transanction='Dépôt',
                                    compte_id=client_compte, date=mise_jr_facture.date, facture=id_facture)
         db.session.add(insert_operation)
      else:
         operations_compte.montant=float(operations_compte.montant) + valeur_de_produit

      if comptes_en_modification.solde is None:
         solde_compte=0
      else:
         solde_compte=float(comptes_en_modification.solde)

      comptes_en_modification.solde= solde_compte + valeur_de_produit

      #Enregistrement et mise à des opération
      db.session.commit()
      if produit_vendu.emballage == 'Carton' or produit_vendu.emballage == 'Box':
         if quantite_par_produit== 0 or quantite_par_produit== 1:
            nbr_quantite_notification=(quantite_vendu/1)
            flash('Vous avez ajouté  {} {} de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
            return redirect(url_for('vente.grosinfofactureacompte'))
         else:
            if produit_vendu.emballage == 'Carton':
               nbr_quantite_notification=round(quantite_vendu/quantite_par_produit,2)
               flash('Vous avez ajouté  {} {} de {}s '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofactureacompte'))
            else:
               nbr_quantite_notification=round(quantite_vendu/quantite_par_produit,2)
               flash('Vous avez ajouté  {} {} de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofactureacompte'))
      else:
         if quantite_vendu > 1 :
            nbr_quantite_notification=quantite_vendu
            if produit_vendu.emballage == 'Vrac':
               flash('Vous avez ajouté  {} Pièces de {} '.format(nbr_quantite_notification,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofactureacompte'))
            else:
               flash('Vous avez ajouté  {} {}s de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofactureacompte'))

         else:
            nbr_quantite_notification=quantite_vendu
            if produit_vendu.emballage == 'Vrac':
               flash('Vous avez ajouté  {} Pièce de {} '.format(nbr_quantite_notification,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofactureacompte'))
            else:
               flash('Vous avez ajouté  {} {} de {} '.format(nbr_quantite_notification,produit_vendu.emballage,produit_vendu.nom_produit),'success')
               return redirect(url_for('vente.grosinfofactureacompte'))

   # INJECTION DANS LE FORMULAIRE
   if request.method=='GET':
      x=0
      x=float(x)
      form.prix_vente_gros.data=x
   
   #LA FACTURE ENCOURS D'ETABLISSEMENT
   facture_encours_etablie=Vente.query.filter(Vente.facture_id==id_facture,Vente.no_facture==False, Vente.montant >=1  ).all()
   facture_donnes=Facture.query.filter_by(id=id_facture).first()
   ver_facture_encours="Vide"
   if facture_encours_etablie is not None:
      ver_facture_encours="NoVide"
   #DIMIUTION SUR LA FACTURE
   dimunition=DiminutionGFactureForm()

   return render_template('vente/vente_cash_detaille_gros_acompte.html',dimunition=dimunition,facture_d=facture_donnes,facture_encours=facture_encours_etablie,ver_facture_encours=ver_facture_encours, option_encours=option_encours, title=title, form=form, id_facture=id_facture)


""" Terminer une facture"""
@vente.route('/acompte/annule_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def annulefactureacompte():
   option_encours='vente'
   title='Vente'
   #Type de la vente
   type_validation_encours=utilitaire.validationacompte()
   vente_acompte_enours=None

   if type_validation_encours is None:
      return redirect(url_for('vente.acompte'))
   else:
      if type_validation_encours==1:
         vente_acompte_enours=True
      else:
         vente_acompte_enours=False
   #Vérification de l'existence de la facture
   if utilitaire.verification_facture()==False:
      if vente_acompte_enours != None:
         return redirect(url_for('vente.acompte'))
   else:
      code_facture=str(utilitaire.verification_facture())
      if vente_acompte_enours != None:
         return redirect(url_for('vente.acompte'))


     
""" Fin de la facture"""
@vente.route('/acompte/fin_facture', methods=['GET','POST'])
@login_required
@autorisation_vendeur
def finfactureaccompte(): 
   #Type de la vente
   type_validation_encours=utilitaire.validationacompte()
   vente_acompte_enours=None

   if type_validation_encours is None:
      return redirect(url_for('vente.acompte'))
   else:
      if type_validation_encours==1:
         vente_acompte_enours=True
      else:
         vente_acompte_enours=False
   #Vérification de l'existence de la facture
   if utilitaire.verification_facture()==False:
      if vente_acompte_enours != None:
         flash('Facture établie','success')
         return redirect(url_for('vente.acompte'))
   else:
      code_facture=str(utilitaire.verification_facture())
      if vente_acompte_enours != None:
         flash('Facture établie','success')
         return redirect(url_for('vente.acompte'))


#--------------------------------------- RAPPORT DES VENTES ADMINISTRATEURS -------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------

""" Option des administrateurs pour les rapports """
@vente.route('/option/admin', methods=['GET'])
@login_required
@autorisation_gerant
def admin_venteindex():
   option_encours='vente'
   title='Rapport des ventes'
   
   series=[]
   profit=[]
   label=[]
   vente_cash=produit_triage_mensuel('Cash')
   
   for i in vente_cash:
      a=i[0]
      b=round(i[2],2)
      c=round(i[4],2)
      label.insert(0,a)
      series.insert(0,b)
      profit.insert(0,c)
      
   
   return render_template('vente/venterapadmin.html',option_encours=option_encours, title=title, label=label, series=series, profit=profit)



""" Option des administrateurs pour les rapports """
@vente.route('/boutique/admin', methods=['GET','POST'])
@login_required
@autorisation_gerant
def admin_vente():
   option_encours='vente'
   title='Rapport des ventes'
   #Sommes de valeurs global
   montant_facture=[]
   valeur_stock=[]
   profit_vente=[]
   #sommes des valeurs cash
   montant_facture_cash=[]
   valeur_stock_cash=[]
   profit_vente_cash=[]
   # Les opération des ventes
   cash_vente=vente_mensuelle('Cash')
   dette_vente=vente_mensuelle('Dette')
   acompte_vente=vente_mensuelle('Acompte')
   #Le profit mensuel global

   mois=date.today()
   separateur=str(mois).split("-")
   annee_encours=f"{separateur[0]}-{separateur[1]}" 

   #Vente cash
   for cash in cash_vente:  
      m=cash[2]
      v=cash[3]
      p=cash[4]
      #Cash 
      mc=cash[2]
      vc=cash[3]
      pc=cash[4]
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
      #Insertion
      montant_facture_cash.insert(0,mc)
      valeur_stock_cash.insert(0,vc)
      profit_vente_cash.insert(0,pc)

   #Vente dette
   for dette in dette_vente:  
      m=dette[2]
      v=dette[3]
      p=dette[4]
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
   
   #Vente dette
   for acompte in acompte_vente:  
      m=acompte[2]
      v=acompte[3]
      p=acompte[4]
      #Acompte
      ma=acompte[2]
      va=acompte[3]
      pa=acompte[4]
      #Insertion dans la facture
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
      #Insers
      montant_facture_cash.insert(0,ma)
      valeur_stock_cash.insert(0,va)
      profit_vente_cash.insert(0,pa)
   vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
   cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]

   return render_template('vente/adminvente.html',option_encours=option_encours, annee_encours=annee_encours, cash_caisse=cash_caisse, vente_global=vente_global, title=title, cash=cash_vente, dette=dette_vente, acompte=acompte_vente)


""" Option des administrateurs pour les rapports """
@vente.route('/boutique/rap/mens/<string:date_vente>', methods=['GET','POST'])
@login_required
@autorisation_gerant
def rapport_mensuel(date_vente):
   #Titre
   title="Rapport mensuel"
   option_encours="vente"
   #Mois d'opértaion
   mois=date.today()
   separateur=str(mois).split("-")
   annee_encours=f"{separateur[0]}-{separateur[1]}" 
   if annee_encours != date_vente:
      flash("Prier de proceder par le filtrage","danger")
      return redirect(url_for('vente.admin_vente'))
   
   # LES FACTURES EN DETAILS

   #Les factures des ventes cash
   cash_detaille=vente_mensuelle_detaille("Cash",date_vente)
   #Les factures des ventes dettes
   dette_detaille=vente_mensuelle_detaille("Dette",date_vente)
   #Les factures des ventes cash
   acompte_detaille=vente_mensuelle_detaille("Acompte",date_vente)

   # LES FACTURES SUR LES GLOBALITES

   #Sommes de valeurs global
   montant_facture=[]
   valeur_stock=[]
   profit_vente=[]
   #sommes des valeurs cash
   montant_facture_cash=[]
   valeur_stock_cash=[]
   profit_vente_cash=[]
   # Les opération des ventes
   cash_vente=vente_mensuelle('Cash')
   dette_vente=vente_mensuelle('Dette')
   acompte_vente=vente_mensuelle('Acompte')
   #Le profit mensuel global
   #Vente cash
   for cash in cash_vente:  
      m=cash[2]
      v=cash[3]
      p=cash[4]
      #Cash 
      mc=cash[2]
      vc=cash[3]
      pc=cash[4]
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
      #Insertion
      montant_facture_cash.insert(0,mc)
      valeur_stock_cash.insert(0,vc)
      profit_vente_cash.insert(0,pc)

   #Vente dette
   for dette in dette_vente:  
      m=dette[2]
      v=dette[3]
      p=dette[4]
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
   
   #Vente dette
   for acompte in acompte_vente:  
      m=acompte[2]
      v=acompte[3]
      p=acompte[4]
      #Acompte
      ma=acompte[2]
      va=acompte[3]
      pa=acompte[4]
      #Insertion dans la facture
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
      #Insers
      montant_facture_cash.insert(0,ma)
      valeur_stock_cash.insert(0,va)
      profit_vente_cash.insert(0,pa)
   vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
   cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]
   
   #Filtrage des donnnes par facture
   form=RechercheFactureRapForm()
   ver_filtre=None
   facture_form=None
   if form.validate_on_submit():

      facture=Facture.query.filter_by(code_facture=form.facture_client.data.code_facture).first()
      ver_filtre=True

      sorte_de_vente=None
      if facture.cash == True:
         sorte_de_vente='Cash'
      elif facture.dette == True:
         sorte_de_vente='Dette'
      elif facture.vente_acompte==True:
         sorte_de_vente='Acompte'
      
      facture_client=[
               facture.id,
               facture.code_facture,
               facture.type_vente,
               float(facture.montant),
               float(facture.valeur_vendue),
               float(facture.montant) - float(facture.valeur_vendue),
               facture.facture_boutique.nom_boutique,
               facture.facture_user.prenom,
               facture.date,
               facture.code_id_facture,
               facture.liquidation,
               sorte_de_vente
               ]
      facture_form=facture_client



   return render_template('vente/adminventerapmen.html',facture=facture_form,ver_filtre=ver_filtre, form=form,option_encours=option_encours, annee_encours=annee_encours,cash=cash_detaille, dette=dette_detaille, acompte=acompte_detaille, vente_global=vente_global, cash_caisse=cash_caisse)

""" Les rapports triers """
@vente.route('/admin/trier/rapport', methods=['GET','POST'])
@login_required
@autorisation_gerant
def trier_rapport():
   #Titre
   title="Rapport trier"
   option_encours="vente"
   #Filtrages les formulaaire de triage
   form=RechercheFactureRapForm()
   trier=RechercheFiltreAdminForm()
   #Les informations
   avant_filtre=None
   #Les variables de verification
   vente_global=None
   cash_caisse=None
   cash_detaille=None
   dette_detaille=None
   acompte_detaille=None
   cash_vente=None
   dette_vente=None
   acompte_vente=None
   date_triage=None
   btq_operation="Toutes les boutiques"
   #Plage
   plage=RecherchePlageAdminForm()
   plage_verification=None
   
   
   if plage.validate_on_submit():
      #Formatage de la date
      date_une=(plage.date_journalier_une.data).split('/')
      date_formatage_une=f"{date_une[2]}-{date_une[1]}-{date_une[0]}"
      # Formatage de la deux 
      date_deux=(plage.date_journalier_deux.data).split('/')
      date_formatage_deux=f"{date_deux[2]}-{date_deux[1]}-{date_deux[0]}"
      
      #Envoie des données 
      session["date_session_une"]=date_formatage_une
      session["date_session_deux"]=date_formatage_deux
      filter_boutique_req=None
      if plage.boutique_triage.data is not None:
         session['boutique']=plage.boutique_triage.data.id
         session['bout_nom']=plage.boutique_triage.data.nom_boutique
         btq_operation=plage.boutique_triage.data.nom_boutique
         filter_boutique_req=plage.boutique_triage.data.id
      else:
         session['boutique']=None
         session['bout_nom']=None
         
      session['verification_plage']=True
      session['date_impression']=f'{plage.date_journalier_une.data}- {plage.date_journalier_deux.data}'
      # LES FACTURES EN DETAILS
      cash_detaille=vente_plage_detaille_boutique("Cash",date_formatage_une,date_formatage_deux, filter_boutique_req)
      dette_detaille=vente_plage_detaille_boutique("Dette",date_formatage_une,date_formatage_deux, filter_boutique_req)
      acompte_detaille=vente_plage_detaille_boutique("Acompte",date_formatage_une,date_formatage_deux, filter_boutique_req)
      #Sommes de valeurs global
      montant_facture=[]
      valeur_stock=[]
      profit_vente=[]
      #sommes des valeurs cash
      montant_facture_cash=[]
      valeur_stock_cash=[]
      profit_vente_cash=[]
      # Les opération des ventes
      cash_vente=vente_plage_triage('Cash',date_formatage_une,date_formatage_deux, filter_boutique_req)
      dette_vente=vente_plage_triage('Dette',date_formatage_une,date_formatage_deux, filter_boutique_req)
      acompte_vente=vente_plage_triage('Acompte',date_formatage_une,date_formatage_deux, filter_boutique_req)
      #Le profit mensuel global
      #Vente cash
      for cash in cash_vente:  
         m=cash[2]
         v=cash[3]
         p=cash[4]
         #Cash 
         mc=cash[2]
         vc=cash[3]
         pc=cash[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insertion
         montant_facture_cash.insert(0,mc)
         valeur_stock_cash.insert(0,vc)
         profit_vente_cash.insert(0,pc)

      #Vente dette
      for dette in dette_vente:  
         m=dette[2]
         v=dette[3]
         p=dette[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
      
      #Vente dette
      for acompte in acompte_vente:  
         m=acompte[2]
         v=acompte[3]
         p=acompte[4]
         #Acompte
         ma=acompte[2]
         va=acompte[3]
         pa=acompte[4]
         #Insertion dans la facture
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insers
         montant_facture_cash.insert(0,ma)
         valeur_stock_cash.insert(0,va)
         profit_vente_cash.insert(0,pa)
      vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
      cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]
      #Formatage du date de l'affichage
      date_triage=f'{plage.date_journalier_une.data}- {plage.date_journalier_deux.data}'
      plage_verification=True
      avant_filtre=True
      
   elif trier.validate_on_submit():
      #Variable de triage
      avant_filtre=True
      #Tableau de vérification des requêtes
      ver_champs=[]
      #Vérification des données dans la liste
      if trier.date_journalier.data !='':
         ver_champs.insert(0,trier.date_journalier.data)
      if trier.date_mensuel.data !='':
         ver_champs.insert(0,trier.date_mensuel.data)
      if trier.date_annuel.data !='':
         ver_champs.insert(0,trier.date_annuel.data)

      #Vérification de longeur de la liste
      if len(ver_champs) > 1 or len(ver_champs) == 0:
         flash("Attention tu dois passer une seule requête seulement","danger")
         return redirect(url_for("vente.trier_rapport"))
      #Envoie des données 
      session["date_session"]=ver_champs[0]
      boutique_id_filter=None
      if trier.boutique_trie.data is not None:
         session['boutique']=trier.boutique_trie.data.id
         session['bout_nom']=trier.boutique_trie.data.nom_boutique
         boutique_id_filter=trier.boutique_trie.data.id
      else:
         session['boutique']=None
         session['bout_nom']=None
      
      session['longeur']=len(ver_champs[0])
      session['verification_plage']=None
         
      # LES FACTURES EN DETAILS
      cash_detaille=vente_mensuelle_detaille_boutique("Cash",ver_champs[0],len(ver_champs[0]), boutique_id_filter)
      dette_detaille=vente_mensuelle_detaille_boutique("Dette",ver_champs[0],len(ver_champs[0]), boutique_id_filter)
      acompte_detaille=vente_mensuelle_detaille_boutique("Acompte",ver_champs[0],len(ver_champs[0]), boutique_id_filter)
      #Sommes de valeurs global
      montant_facture=[]
      valeur_stock=[]
      profit_vente=[]
      #sommes des valeurs cash
      montant_facture_cash=[]
      valeur_stock_cash=[]
      profit_vente_cash=[]
      # Les opération des ventes
      cash_vente=vente_mensuelle_triage('Cash',ver_champs[0],len(ver_champs[0]), trier.boutique_trie.data)
      dette_vente=vente_mensuelle_triage('Dette',ver_champs[0],len(ver_champs[0]), trier.boutique_trie.data)
      acompte_vente=vente_mensuelle_triage('Acompte',ver_champs[0],len(ver_champs[0]), trier.boutique_trie.data)
      #Le profit mensuel global
      #Vente cash
      for cash in cash_vente:  
         m=cash[2]
         v=cash[3]
         p=cash[4]
         #Cash 
         mc=cash[2]
         vc=cash[3]
         pc=cash[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insertion
         montant_facture_cash.insert(0,mc)
         valeur_stock_cash.insert(0,vc)
         profit_vente_cash.insert(0,pc)

      #Vente dette
      for dette in dette_vente:  
         m=dette[2]
         v=dette[3]
         p=dette[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
      
      #Vente dette
      for acompte in acompte_vente:  
         m=acompte[2]
         v=acompte[3]
         p=acompte[4]
         #Acompte
         ma=acompte[2]
         va=acompte[3]
         pa=acompte[4]
         #Insertion dans la facture
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insers
         montant_facture_cash.insert(0,ma)
         valeur_stock_cash.insert(0,va)
         profit_vente_cash.insert(0,pa)
      vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
      cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]
      #Formatage du date de l'affichage
      date_triage=ver_champs[0]
      if trier.boutique_trie.data is not None:
         btq_operation=trier.boutique_trie.data.nom_boutique


   return render_template('vente/rapadmintrier.html',btq_operation=btq_operation, plage_verification=plage_verification, plage=plage, date_operation=date_triage,vente_global=vente_global, cash_caisse=cash_caisse, title=title, option_encours=option_encours, form=form, trier=trier, avant_filtre=avant_filtre, cash=cash_detaille, dette=dette_detaille, acompte=acompte_detaille)


"""Les rapports trié par les requêtes de produit"""
@vente.route('/admin/produit', methods=['GET','POST'])
@login_required
@autorisation_gerant
def produit_req():
   #Titre du produit
   title="Rapport"
   option_encours="vente"
   # Les types des ventes
   vente_cash=produit_triage_mensuel('Cash')
   vente_dette=produit_triage_mensuel('Dette')
   vente_acompte=produit_triage_mensuel('Acompte')
   
   return render_template("vente/rapproduit.html", title=title, option_encours=option_encours, cash=vente_cash, dette=vente_dette, acompte=vente_acompte )



"""Les produits filtrés par boutique"""
@vente.route('/admin/filtre/produit', methods=['GET','POST'])
@login_required
@autorisation_gerant
def produit_req_filtre():
   #Titre du produit
   title="Rapport"
   option_encours="vente"
   # Les types des ventes
   trier=RechercheFiltreAdminProForm()
   plage=RecherchePlageAdminProduiForm()
   avant_filtre=None
   
   date_operation=None
   boutique_operation=None
   produit_req_boutique=None
   
   boutique_requete=None
   nom_boutique_triage=None
   produit_boutique=None
   
   vente_cash=None
   vente_dette=None
   vente_acompte=None
   
   triage=None
   plage_verification=None
     
   if plage.validate_on_submit():
       
      #Formatage de la date
      date_une=(plage.date_journalier_une.data).split('/')
      date_formatage_une=f"{date_une[2]}-{date_une[1]}-{date_une[0]}"
      # Formatage de la deux 
      date_deux=(plage.date_journalier_deux.data).split('/')
      date_formatage_deux=f"{date_deux[2]}-{date_deux[1]}-{date_deux[0]}"
      #Tableau des opérations
      operation_date=[date_formatage_une,date_formatage_deux]
      #Boutique
      boutique_requete=None
      boutique_operation="Toutes les boutiques"
      if plage.boutique_triage.data is not None:
         boutique_requete=plage.boutique_triage.data.id
         nom_boutique_triage=plage.boutique_triage.data.nom_boutique
         
      #Produit
      produit_boutique=None
      if plage.produit_triage.data is not None:
         produit_boutique=plage.produit_triage.data.nom_produit
      # LES FACTURES EN DETAILS
      vente_cash=vente_plage_triage_admin("Cash",operation_date,boutique_requete,produit_boutique)
      vente_dette=vente_plage_triage_admin("Dette",operation_date,boutique_requete,produit_boutique)
      vente_acompte=vente_plage_triage_admin("Acompte",operation_date,boutique_requete,produit_boutique)
      
      #Formatage du date de l'affichage
      date_operation=f'{plage.date_journalier_une.data}- {plage.date_journalier_deux.data}'
      plage_verification=True
      avant_filtre=True
   elif trier.validate_on_submit():
      #Variable de triage
      avant_filtre=True
      #Tableau de vérification des requêtes
      ver_champs=[]
      #Vérification des données dans la liste
      if trier.date_journalier.data !='':
         ver_champs.insert(0,trier.date_journalier.data)
      if trier.date_mensuel.data !='':
         ver_champs.insert(0,trier.date_mensuel.data)
      if trier.date_annuel.data !='':
         ver_champs.insert(0,trier.date_annuel.data)

      if len(ver_champs) > 1 or len(ver_champs) == 0:
         flash("Attention tu dois passer une seule requête seulement","danger")
         return redirect(url_for("vente.produit_req_filtre"))
      # Formatage de la date
      format_date=None
      date_format=str(ver_champs[0]).split("/")
      if len(ver_champs[0]) == 10:
         format_date=f'{date_format[2]}-{date_format[1]}-{date_format[0]}'
      if len(ver_champs[0]) == 7:
         format_date=f'{date_format[1]}-{date_format[0]}'
      if len(ver_champs[0]) == 4:
         format_date=str(ver_champs[0])
      #Triage de la boutique
      triage=True
      #Vérification de la boutique
      produit_req_boutique=None
      id_boutique_pro=None
      if trier.produit_triage.data is not None:
         produit_req_boutique=trier.produit_triage.data.nom_produit
         id_boutique_pro=trier.boutique_trie.data.id
          
      vente_cash=produit_triage_par_option('Cash',format_date,trier.boutique_trie.data, produit_req_boutique)
      vente_dette=produit_triage_par_option('Dette',format_date,trier.boutique_trie.data, produit_req_boutique)
      vente_acompte=produit_triage_par_option('Acompte',format_date,trier.boutique_trie.data, produit_req_boutique)
      #Les information d'affichage
      date_operation=ver_champs[0]
      
      if trier.boutique_trie.data is not None:
         boutique_operation=trier.boutique_trie.data.nom_boutique
      else:
         boutique_operation="Toutes les boutiques"
      #Vérification des session
      session['date_format']=format_date
      session['veri_boutique']=id_boutique_pro
      session['boutique_produit']=produit_req_boutique
      session["triage"]=triage
   
   return render_template("vente/rapproduitfiltre.html",produit_req_boutique=produit_boutique, date_operation=date_operation,avant_filtre=avant_filtre, boutique_operation=boutique_operation, plage=plage, trier=trier, title=title, option_encours=option_encours, cash=vente_cash, dette=vente_dette, acompte=vente_acompte )




#------------------------------------------------------------------LES IMPRESSIONS ------------------------------------
""" Option des administrateurs pour les rapports """
@vente.route('/boutique/rap/mens/impr/<string:date_vente>', methods=['GET','POST'])
@login_required
@autorisation_gerant
def imp_rapport_mensuel(date_vente):
   #Titre
   title="Rapport mensuel"
   option_encours="vente"
   #Mois d'opértaion
   mois=date.today()
   separateur=str(mois).split("-")
   annee_encours=f"{separateur[0]}-{separateur[1]}" 
   if annee_encours != date_vente:
      flash("Prier de proceder par le filtrage","danger")
      return redirect(url_for('vente.admin_vente'))
   
   # LES FACTURES EN DETAILS

   #Les factures des ventes cash
   cash_detaille=vente_mensuelle_detaille("Cash",date_vente)
   #Les factures des ventes dettes
   dette_detaille=vente_mensuelle_detaille("Dette",date_vente)
   #Les factures des ventes cash
   acompte_detaille=vente_mensuelle_detaille("Acompte",date_vente)

   # LES FACTURES SUR LES GLOBALITES

   #Sommes de valeurs global
   montant_facture=[]
   valeur_stock=[]
   profit_vente=[]
   #sommes des valeurs cash
   montant_facture_cash=[]
   valeur_stock_cash=[]
   profit_vente_cash=[]
   # Les opération des ventes
   cash_vente=vente_mensuelle('Cash')
   dette_vente=vente_mensuelle('Dette')
   acompte_vente=vente_mensuelle('Acompte')
   #Le profit mensuel global
   #Vente cash
   for cash in cash_vente:  
      m=cash[2]
      v=cash[3]
      p=cash[4]
      #Cash 
      mc=cash[2]
      vc=cash[3]
      pc=cash[4]
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
      #Insertion
      montant_facture_cash.insert(0,mc)
      valeur_stock_cash.insert(0,vc)
      profit_vente_cash.insert(0,pc)

   #Vente dette
   for dette in dette_vente:  
      m=dette[2]
      v=dette[3]
      p=dette[4]
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
   
   #Vente dette
   for acompte in acompte_vente:  
      m=acompte[2]
      v=acompte[3]
      p=acompte[4]
      #Acompte
      ma=acompte[2]
      va=acompte[3]
      pa=acompte[4]
      #Insertion dans la facture
      montant_facture.insert(0,m)
      valeur_stock.insert(0,v)
      profit_vente.insert(0,p)
      #Insers
      montant_facture_cash.insert(0,ma)
      valeur_stock_cash.insert(0,va)
      profit_vente_cash.insert(0,pa)
   vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
   cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]
   
   return render_template('vente/impr_rap_mens.html',option_encours=option_encours, cash=cash_detaille, dette=dette_detaille, acompte=acompte_detaille, vente_global=vente_global, cash_caisse=cash_caisse)


""" Les rapports triers """
@vente.route('/admin/trier/rapport/impr', methods=['GET','POST'])
@login_required
@autorisation_gerant
def impri_trier_rapport():
   #Titre
   title="Rapport trier"
   option_encours="vente"


   #Les informations
   avant_filtre=None
   #Les variables de verification
   vente_global=None
   cash_caisse=None
   cash_detaille=None
   dette_detaille=None
   acompte_detaille=None
   cash_vente=None
   dette_vente=None
   acompte_vente=None
   date_triage=None
   bouttique_op=None

   date_op_impri=None
   boutique_op_impri=None
   long_op_impri=None
   nom_boutique_impr=None

  #Plage de date
   verification_plage=None
   date_une=None
   date_deux=None
   date_session_une=None
   date_session_deux=None
   boutique=None
   bout_nom=None
   date_op_imprimer=None
   
  
   if 'verification_plage' in session:
      verification_plage=session['verification_plage']

   if verification_plage == True:
      if 'date_session_une' in session:
         date_session_une=session['date_session_une']
      
      if 'date_session_deux' in session:
         date_session_deux=session['date_session_deux']
         
      if 'boutique' in session:
         boutique=session['boutique']
      
      if 'bout_nom' in session:
         bout_nom=session['bout_nom']
      
      if 'date_impression' in session:
         date_op_imprimer=session['date_impression']


      
      

      # LES FACTURES EN DETAILS
      cash_detaille=vente_plage_detaille_boutique("Cash",date_session_une,date_session_deux,boutique)
      dette_detaille=vente_plage_detaille_boutique("Dette",date_session_une,date_session_deux,boutique)
      acompte_detaille=vente_plage_detaille_boutique("Acompte",date_session_une,date_session_deux,boutique)
      #Sommes de valeurs global
      montant_facture=[]
      valeur_stock=[]
      profit_vente=[]
      #sommes des valeurs cash
      montant_facture_cash=[]
      valeur_stock_cash=[]
      profit_vente_cash=[]
      # Les opération des ventes
      cash_vente=vente_plage_triage('Cash',date_session_une,date_session_deux,boutique)
      dette_vente=vente_plage_triage('Dette',date_session_une,date_session_deux,boutique)
      acompte_vente=vente_plage_triage('Acompte',date_session_une,date_session_deux,boutique)
      #Le profit mensuel global
      #Vente cash
      for cash in cash_vente:  
         m=cash[2]
         v=cash[3]
         p=cash[4]
         #Cash 
         mc=cash[2]
         vc=cash[3]
         pc=cash[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insertion
         montant_facture_cash.insert(0,mc)
         valeur_stock_cash.insert(0,vc)
         profit_vente_cash.insert(0,pc)

      #Vente dette
      for dette in dette_vente:  
         m=dette[2]
         v=dette[3]
         p=dette[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
      
      #Vente dette
      for acompte in acompte_vente:  
         m=acompte[2]
         v=acompte[3]
         p=acompte[4]
         #Acompte
         ma=acompte[2]
         va=acompte[3]
         pa=acompte[4]
         #Insertion dans la facture
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insers
         montant_facture_cash.insert(0,ma)
         valeur_stock_cash.insert(0,va)
         profit_vente_cash.insert(0,pa)
      vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
      cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]
      #Formatage du date de l'affichage
      date_triage=date_op_imprimer
      bouttique_op=bout_nom
      plage_verification=True
      avant_filtre=True
   else:

      #Envoie des données 
      if 'date_session' in session:
         date_op_impri=session['date_session']
         
      if 'boutique' in session:
         boutique_op_impri=session['boutique']
         
      if 'longeur' in session:
         long_op_impri=session['longeur']
      
      if 'bout_nom' in session:
         nom_boutique_impr=session['bout_nom']

      print(boutique_op_impri,'yyyyyyyyyyyyyyyyqsdddddddddddddddyjjjjjjjjjjjjjjjjjjjjjjjdqqqqqqqqqqqqqq')
      # LES FACTURES EN DETAILS
      cash_detaille=vente_mensuelle_detaille_boutique("Cash",date_op_impri,long_op_impri, boutique_op_impri)
      dette_detaille=vente_mensuelle_detaille_boutique("Dette",date_op_impri,long_op_impri, boutique_op_impri)
      acompte_detaille=vente_mensuelle_detaille_boutique("Acompte",date_op_impri,long_op_impri, boutique_op_impri)
      #Sommes de valeurs global
      montant_facture=[]
      valeur_stock=[]
      profit_vente=[]
      #sommes des valeurs cash
      montant_facture_cash=[]
      valeur_stock_cash=[]
      profit_vente_cash=[]
      # Les opération des ventes
      cash_vente=vente_mensuelle_triage("Cash",date_op_impri,long_op_impri, boutique_op_impri)
      dette_vente=vente_mensuelle_triage("Dette",date_op_impri,long_op_impri, boutique_op_impri)
      acompte_vente=vente_mensuelle_triage("Acompte",date_op_impri,long_op_impri, boutique_op_impri)
      #Le profit mensuel global
         
      #Vente cash
      for cash in cash_vente:  
         m=cash[2]
         v=cash[3]
         p=cash[4]
         #Cash 
         mc=cash[2]
         vc=cash[3]
         pc=cash[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         #Insertion
         montant_facture_cash.insert(0,mc)
         valeur_stock_cash.insert(0,vc)
         profit_vente_cash.insert(0,pc)

         #Vente dette
      for dette in dette_vente:  
         m=dette[2]
         v=dette[3]
         p=dette[4]
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
         
         #Vente dette
      for acompte in acompte_vente:  
         m=acompte[2]
         v=acompte[3]
         p=acompte[4]
         #Acompte
         ma=acompte[2]
         va=acompte[3]
         pa=acompte[4]
         #Insertion dans la facture
         montant_facture.insert(0,m)
         valeur_stock.insert(0,v)
         profit_vente.insert(0,p)
            #Insers
         montant_facture_cash.insert(0,ma)
         valeur_stock_cash.insert(0,va)
         profit_vente_cash.insert(0,pa)
      vente_global=[sum(montant_facture), sum(valeur_stock), sum(profit_vente)]
      cash_caisse=[sum(montant_facture_cash), sum(valeur_stock_cash), sum(profit_vente_cash)]
      #Formatage du date de l'affichage
      date_triage=date_op_impri
      bouttique_op=nom_boutique_impr
     
   if bouttique_op is None:
      bouttique_op="Toutes les boutiques"
   return render_template('vente/impr_rap_filtre.html',verification_plage=verification_plage, bouttique_op=bouttique_op, date_operation=date_triage,vente_global=vente_global, cash_caisse=cash_caisse, title=title, option_encours=option_encours, avant_filtre=avant_filtre, cash=cash_detaille, dette=dette_detaille, acompte=acompte_detaille)


