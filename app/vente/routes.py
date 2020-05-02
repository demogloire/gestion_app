from flask import render_template, flash, url_for, redirect, request, session, g
from .. import db, bcrypt
from ..models import User, Boutique, Depot, Stock, Produit, Produitboutique, Facture, Vente, Payement, Operation, Comptes
from app.vente.forms import FactureForm, VenteFactureForm, RechercheForm, FactureAcForm,  PayementFactureForm,  DiminutionFactureForm, RechercheAFactureForm,  VenteFactureGForm, DiminutionGFactureForm, RechercheFactureForm, RechercheDFactureForm
import app.pack_fonction.fonction as utilitaire
from app.vente.autorisation import autorisation_vendeur
from datetime import datetime, date
from flask_login import login_user, current_user, login_required
from sqlalchemy import func




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
   #Vérification de l'existence de la facture pour le client
   if facture_encours is None:
      flash("Attention cette opération est dangereuse","danger")
      return redirect(url_for('vente.cash'))
   
   #Vérification de la vente encours
   vente_encours=Vente.query.filter_by(facture_id=facture).all()

   #Session de supression de la facture sur la plateforme
   an_facture_encours=None
   if 'annuler_facture' in session:
      an_facture_encours=session['annuler_facture']

   #ANNULATION DE LA FACTURE
   for an_fact in vente_encours:
      #Quantité à diminuer dans la facture
      quantite=an_fact.quantite
      #DIMINUTION PROPREMENDITE
      quantite_vente_encours=an_fact.quantite
      quantite_entree = quantite
      #Soustraction
      nouvelle_quantite=quantite_vente_encours - quantite_entree
      nv=quantite* an_fact.prix_unitaire
      valeur=nv
      #Enregistrement de la diminution de la vente
      an_fact.quantite=nouvelle_quantite
      an_fact.montant=valeur
      an_fact.no_facture=True

      #FACTURE ENCOURS
      nv_f=facture_encours.montant - valeur
      #Soustraction
      facture_encours.montant=nv_f

      #SOCK DISPONIBLE
      id_produit_encours=an_fact.produitboutique_id
      ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_encours, boutique_id=current_user.boutique_id, solde=True).first()
      ver_stock.solde=False
      #Les variable de stockage
      qte_stock_encours=ver_stock.disponible + quantite
      quantite_valeur_op=quantite*an_fact.prix_unitaire# La valeur de l'opération
      valeurs_nouvelle_dispo= ver_stock.valeur_dispo + quantite_valeur_op

      #ENREGSITREMENT DU SOCKAGE
      stockage_boutique=Stock(quantite=quantite, valeur=quantite_valeur_op, datest=facture_encours.date, prix_unit=an_fact.prix_unitaire, 
                        disponible=qte_stock_encours, 
                        valeur_dispo=valeurs_nouvelle_dispo, facture_annule=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
      db.session.add(stockage_boutique)
      db.session.commit()
   
   if an_facture_encours == True:
      flash("Vous aviez annulé la facture {}".format(facture_encours.code_facture),'success')
      return redirect(url_for('vente.cash'))
   elif an_facture_encours == False:
      flash("Vous aviez annulé la facture {}".format(facture_encours.code_facture),'success')
      return redirect(url_for('vente.dette'))
   else:
      flash("Prière de respecter la procedure",'danger')


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
            prix_op_vente=float(produit_vendu.vt_detaille_piece/nbr_cont_pro)   # Prix en fonction de produit
         else:
            prix_op_vente=produit_vendu.vt_detaille_piece
      else:
         prix_op_vente=prix_du_produit #Prix en fonction de la variation
      #Valeur de la transanction
      valeur_de_produit=float(prix_op_vente*quantite_vendu)

      #OPERATION DE STOCKAGE 
      stock_disponible_boutique=stockage_produit.disponible - quantite_vendu
      prix_unitaire_stock=stockage_produit.valeur_dispo/stockage_produit.disponible
      valeur_de_produit_sock=float(prix_unitaire_stock*stock_disponible_boutique)

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
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant ) + valeur_de_produit
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

      valeur_entree_sous=quantite * vente_encours.prix_unitaire
      
      #DIMINUTION PROPREMENDITE
      if vente_encours.quantite >=quantite:
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

   #ENREGSITREMENT DU SOCKAGE
   stockage_boutique=Stock(quantite=quantite, valeur=quantite_valeur_op, datest=facture_encours.date, prix_unit=vente_encours.prix_unitaire, 
                     disponible=qte_stock_encours, 
                     valeur_dispo=valeurs_nouvelle_dispo, facture_annule=True, boutique_id=current_user.boutique_id, 
                     stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
   db.session.add(stockage_boutique)
   db.session.commit()
   flash("Vous avez supprime le {} sur la facture".format(vente_encours.vente_produitboutique.nom_produit),"success")
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
   db.session.commit()
   flash("Vous avez supprime le {} sur la facture".format(vente_encours.vente_produitboutique.nom_produit),"success")
   if cash_dette_encours==False:
      return redirect(url_for('vente.infofactureacompte'))
   else:
      return redirect(url_for('vente.infofactureacompte'))








""" Impression facture"""
@vente.route('/imp-<int:facture>', methods=['GET','POST'])
@login_required
@autorisation_vendeur
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
@autorisation_vendeur
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
@autorisation_vendeur
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
@autorisation_vendeur
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
@autorisation_vendeur
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
@autorisation_vendeur
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
@autorisation_vendeur
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

      #OPERATION DE STOCKAGE 
      stock_disponible_boutique=stockage_produit.disponible - quantite_vendu
      prix_unitaire_stock=float(stockage_produit.valeur_dispo)/float(stockage_produit.disponible)
      valeur_de_produit_sock=prix_unitaire_stock*stock_disponible_boutique

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
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant) + valeur_de_produit
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
         
      valeur_entree_sous=quantite * float(vente_encours.prix_unitaire)

      #DIMINUTION PROPREMENDITE
      if vente_encours.quantite >= quantite:
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
         #SOCK DISPONIBLE
         id_produit_encours=vente_encours.produitboutique_id
         ver_stock=Stock.query.filter_by(produitboutique_id=id_produit_encours, boutique_id=current_user.boutique_id, solde=True).first()
         ver_stock.solde=False
         #Les variable de stockage
         qte_stock_encours=ver_stock.disponible + quantite
         quantite_valeur_op=quantite* float(vente_encours.prix_unitaire) # La valeur de l'opération
         valeurs_nouvelle_dispo= float(ver_stock.valeur_dispo) + quantite_valeur_op

         #ENREGSITREMENT DU SOCKAGE
         stockage_boutique=Stock(quantite=quantite, valeur=quantite_valeur_op, datest=facture_encours.date, prix_unit=vente_encours.prix_unitaire, 
                           disponible=qte_stock_encours, 
                           valeur_dispo=valeurs_nouvelle_dispo, facture_annule=True, boutique_id=current_user.boutique_id, 
                           stock_user=current_user, produitboutique_id=id_produit_encours, solde=True)
         db.session.add(stockage_boutique)
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
      
      if montant_global_payement== 0:
         paiement_facture=Payement(code_payement=nouveau_code_facture,montant=montant_payer,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
      else:
         paiement_facture=Payement(code_payement=nouveau_code_facture,liquidation=True, montant=montant_payer,denomination=message_dela_facture,date=aujourd,facture_id=facture_dimunition.id)
      db.session.add(paiement_facture)
      # Dimunition de la facture
      facture_dimunition.liquidation=True
      facture_dimunition.montant=montant_global_payement
      operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id,liquidation=True, montant=montant_payer, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente)
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
      
   if montant_global_payement== 0:
      paiement_facture=Payement(code_payement=nouveau_code_facture,montant=montant_payer,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
   else:
      paiement_facture=Payement(code_payement=nouveau_code_facture,liquidation=True, montant=montant_payer,denomination=message_dela_facture,date=aujourd,facture_id=facture_dimunition.id)
   db.session.add(paiement_facture)
   # Dimunition de la facture
   facture_dimunition.liquidation=True
   facture_dimunition.montant=montant_global_payement
   operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id, liquidation=True, montant=montant_payer, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente)
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
         operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id, liquidation=True, montant=montant_global, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente)
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

            paiement_facture=Payement(code_payement=nouveau_code_facture,montant=solde_client_compte,denomination=message_dela_facture,date=aujourd, liquidation=True, facture_id=facture_dimunition.id)
            facture_dimunition.liquidation=True
            facture_dimunition.montant= montant_global_payement
            operation_facture=Facture(code_facture=nouveau_code_facture, code_id_facture=facture_dimunition.id, liquidation=True, montant=solde_client_compte, date=aujourd, cash=True, client_id=facture_dimunition.client_id, user_id=current_user.id, boutique_id=facture_dimunition.boutique_id, type_vente=facture_dimunition.type_vente)
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
            prix_op_vente=float(produit_vendu.vt_detaille_piece/nbr_cont_pro)   # Prix en fonction de produit
         else:
            prix_op_vente=produit_vendu.vt_detaille_piece
      else:
         prix_op_vente=prix_du_produit #Prix en fonction de la variation
      #Valeur de la transanction
      valeur_de_produit=float(prix_op_vente*quantite_vendu)
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


      # MISE A JOUR DE LA FACTURE
      mise_jr_facture=Facture.query.filter_by(id=id_facture).first()
      if mise_jr_facture.montant is None:
         mise_jr_facture.montant=valeur_de_produit
      else:
         mise_jr_facture.montant=float(mise_jr_facture.montant ) + valeur_de_produit
      
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

   le_stock_insuffisant=[]

   aujourd=date.today()
   #ANNULATION DE LA FACTURE
   for an_fact in vente_encours:
      stockage_produit=Stock.query.filter_by(produitboutique_id=an_fact.vente_produitboutique.id, boutique_id=current_user.boutique_id, solde=True).first()
      
      if facture_encours.valide_account==True:
      #Le produit 
         valeur= float(an_fact.prix_unitaire) * float(an_fact.quantite)
         disponible_stock=stockage_produit.disponible + an_fact.quantite
         valeur_dispo_acompte= float(stockage_produit.valeur_dispo) + valeur
         stockage_produit.solde=False
         stockage_boutique=Stock(quantite=an_fact.quantite, valeur=valeur, datest=aujourd, prix_unit=an_fact.prix_unitaire, 
                        disponible=disponible_stock, valeur_dispo=valeur_dispo_acompte, vente_boutique=True, boutique_id=current_user.boutique_id, 
                        stock_user=current_user, produitboutique_id=an_fact.vente_produitboutique.id, solde=True)
         db.session.add(stockage_boutique)
         Vente.query.filter_by(id=an_fact.id).delete()
         db.session.commit()
      else:
         Vente.query.filter_by(id=an_fact.id).delete()
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
