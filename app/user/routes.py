from flask import render_template, flash, url_for, redirect, request, session, g
from .. import db, bcrypt
from ..models import User, Boutique, Depot
from app.user.forms import AjoutUserForm, EditUserForm, PassuserForm
from app.user.utility import save_picture, verification_de_role
from flask_login import login_user, current_user, login_required



import flask_sijax
from . import user

""" Ajout utilisateur"""
@user.route('/ajouter_utilisateur', methods=['GET','POST'])
@login_required
def ajouterutilisateur():
   #Un utilisateur
   form=AjoutUserForm()
   #Titre de l'onglet
   title="Les utilisateurs"
   #Vérification du droit général
   droit_general_boutique=Boutique.query.filter_by(nom_boutique='Aucun').first()
   droit_general_depot=Depot.query.filter_by(nom_depot='Aucun').first()
   if droit_general_boutique is None and droit_general_depot is None :
      boutique=Boutique(nom_boutique='Aucun')
      depot=Depot(nom_depot='Aucun')
      db.session.add(depot)
      db.session.add(boutique)
      db.session.commit()

      
   #Envoi de formulaire par la methode POST
   if form.validate_on_submit():
      password_user=form.password.data
      password_hash=bcrypt.generate_password_hash(password_user).decode('utf-8') #génération du password Hacher

      id_boutique=None
      id_depot=None

      #Verification d'association boutique
      if form.depot_users.data.nom_depot=="Aucun":
         pass
      else:
         id_depot=form.depot_users.data.id

      #Vérification d'association du boutique
      if form.boutique_users.data.nom_boutique=="Aucun":
         pass
      else:
         id_boutique=form.boutique_users.data.id

      ver_role=verification_de_role(form.role.data,form.boutique_users.data.nom_boutique,form.depot_users.data.nom_depot)
      if ver_role=="Faux":
         return redirect(url_for('user.ajouterutilisateur'))
      else:
         pass
         
      if form.avatar.data:
         avatar_user=save_picture(form.avatar.data) #reduction de la taille de l'image
         #Enregistrement d'un utilisateur
         user_nv=User(nom=form.nom.data.upper(), post_nom=form.post_nom.data.upper(), prenom=form.prenom.data.capitalize(),\
         adress=form.adress.data, tel=form.tel.data, email=form.email.data,\
         password=password_hash, password_onhash=form.password.data, depot_id=id_depot,\
         boutique_id=id_boutique,avatar=avatar_user,role=form.role.data,statut=True)
         db.session.add(user_nv)
         db.session.commit()
         flash("Vous avez ajouté un utilisateur",'success')
         return redirect(url_for('user.index'))
      else:
         user_nv=User(nom=form.nom.data.upper(), post_nom=form.post_nom.data.upper(), prenom=form.prenom.data.capitalize(),\
         adress=form.adress.data, tel=form.tel.data, email=form.email.data,\
         password=password_hash, password_onhash=form.password.data, depot_id=id_depot,\
         boutique_id=id_boutique,role=form.role.data,statut=True)
         db.session.add(user_nv)
         db.session.commit()
         flash("Vous avez ajouté un utilisateur",'success')
         return redirect(url_for('user.index'))
   return render_template('user/utilisateur.html', form=form, title=title)

@user.route('/')
@login_required
def index():
   #Titre de l'onglet
   title="Liste des utlisateurs"
   #Requête d'affichage des utilsiateurs
   listes=User.query.order_by(User.id.desc())
   return render_template('user/index.html',title=title, liste=listes)


"""Statut de l'utilisateur"""
@user.route('/activation/<int:id_user>/utilisateur',methods=('GET', 'POST') )
@login_required
def activationuser(id_user):
   #Vérification de l'existence de l'utilisateur
   user_profil=User.query.filter_by(id=id_user).first_or_404()
   #Vérification de l'état du statut
   if user_profil.statut==True:
      user_profil.statut=False
      db.session.commit()
      flash("Vous avez désactivé l'utilisateur", "success")
      return redirect(url_for('user.index'))
   else:
      user_profil.statut=True
      db.session.commit()
      flash("Vous avez activé l'utilisateur", "success")
      return redirect(url_for('user.index'))
   return render_template('user/index.html')

""" Ajout utilisateur"""
@user.route('/miseajour/<int:id_user>', methods=['GET','POST'])
@login_required
def miseajour_utilisateur(id_user):
   #Un utilisateur
   form=EditUserForm()
   form_pass=PassuserForm()
   #Titre de l'onglet
   title="Les utilisateurs"

   #Vérification de l'existence de l'utilisateur
   user_profil=User.query.filter_by(id=id_user).first_or_404()
   title=" {} | Modification".format(user_profil.prenom)

   prenom=" {} ".format(user_profil.prenom)

   #Envoi de formulaire par la methode POST
   if form.validate_on_submit():
      
      id_boutique=None
      id_depot=None

      #Verification d'association boutique
      if form.depot_users.data.nom_depot=="Aucun":
         pass
      else:
         id_depot=form.depot_users.data.id

      #Vérification d'association du boutique
      if form.boutique_users.data.nom_boutique=="Aucun":
         pass
      else:
         id_boutique=form.boutique_users.data.id

      ver_role=verification_de_role(form.role.data,form.boutique_users.data.nom_boutique,form.depot_users.data.nom_depot)

      if ver_role == "Faux":
         return redirect(url_for('user.miseajour_utilisateur', id_user=id_user))
      else:
         pass
         
      if form.avatar.data:
         avatar_user=save_picture(form.avatar.data) #reduction de la taille de l'image
         #Modification de l'utilisateur
         if user_profil.email==form.email.data:
            user_profil.nom=form.nom.data.upper()
            user_profil.post_nom=form.post_nom.data.upper()
            user_profil.prenom=form.prenom.data.capitalize()
            user_profil.adress=form.adress.data
            user_profil.tel=form.tel.data
            user_profil.boutique_id=id_boutique
            user_profil.depot_id=id_depot
            user_profil.avatar=avatar_user
            user_profil.role=form.role.data
            db.session.commit()
            flash("Vous avez modifié les informations de {} ".format(form.nom.data.upper()),'success')
            return redirect(url_for('user.index'))
         else:
            user_profil.nom=form.nom.data.upper()
            user_profil.post_nom=form.post_nom.data.upper()
            user_profil.prenom=form.prenom.data.capitalize()
            user_profil.adress=form.adress.data
            user_profil.tel=form.tel.data
            user_profil.email=form.email.data
            user_profil.boutique_id=id_boutique
            user_profil.depot_id=id_depot
            user_profil.avatar=avatar_user
            user_profil.role=form.role.data
            db.session.commit()
            flash("Vous avez modifié les informations de {} ".format(form.nom.data.upper()),'success')
            return redirect(url_for('user.index'))

      else:
         #Modification de l'utlisateur
         if user_profil.email==form.email.data:
            user_profil.nom=form.nom.data.upper()
            user_profil.post_nom=form.post_nom.data.upper()
            user_profil.prenom=form.prenom.data.capitalize()
            user_profil.adress=form.adress.data
            user_profil.tel=form.tel.data
            user_profil.boutique_id=id_boutique
            user_profil.depot_id=id_depot
            user_profil.role=form.role.data
            db.session.commit()
            flash("Vous avez modifié les informations de {} ".format(form.nom.data.upper()),'success')
            return redirect(url_for('user.index'))
         else:
            user_profil.nom=form.nom.data.upper()
            user_profil.post_nom=form.post_nom.data.upper()
            user_profil.prenom=form.prenom.data.capitalize()
            user_profil.adress=form.adress.data
            user_profil.tel=form.tel.data
            user_profil.boutique_id=id_boutique
            user_profil.depot_id=id_depot
            user_profil.email=form.email.data
            user_profil.role=form.role.data
            db.session.commit()
            flash("Vous avez modifié les informations de {} ".format(form.nom.data.upper()),'success')
            return redirect(url_for('user.index'))
   
   if form_pass.validate_on_submit():
      password_user=form_pass.password.data
      password_hash=bcrypt.generate_password_hash(password_user).decode('utf-8') #génération du password Hacher
      #Modification du mot de passe
      user_profil.password=password_hash
      user_profil.password_onhash=password_user
      db.session.commit()
      flash("Vous avez modifié le mot de passe", "success")
      return redirect(url_for('user.index'))


   if request.method=='GET':
         form.nom.data=user_profil.nom
         form.post_nom.data=user_profil.post_nom
         form.prenom.data=user_profil.prenom
         form.adress.data=user_profil.adress
         form.tel.data=user_profil.tel
         form.email.data=user_profil.email
         form.boutique_users.data=user_profil.user_boutique   
         form.depot_users.data=user_profil.user_depot 
         form.role.data=user_profil.role

   return render_template('user/mod_utilisateur.html', form=form, title=title, prenom=prenom, form_pass=form_pass)


