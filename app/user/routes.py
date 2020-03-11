from flask import render_template, flash, url_for, redirect, request, session
from .. import db, bcrypt
from ..models import User, Boutique, Depot
from app.user.forms import AjoutUserForm
from app.user.utility import save_picture, verification_de_role
from flask_login import login_user, current_user, login_required


from . import user

""" Ajout utilisateur"""
@user.route('/ajouter_utilisateur', methods=['GET','POST'])
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
      if ver_role is None:
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
      else:
         user_nv=User(nom=form.nom.data.upper(), post_nom=form.post_nom.data.upper(), prenom=form.prenom.data.capitalize(),\
         adress=form.adress.data, tel=form.tel.data, email=form.email.data,\
         password=password_hash, password_onhash=form.password.data, depot_id=id_depot,\
         boutique_id=id_boutique,role=form.role.data,statut=True)
         db.session.add(user_nv)
         db.session.commit()
   return render_template('user/utilisateur.html', form=form, title=title)




# """ Ajout des collaborateurs sur la plateforme """

# @user.route('/ajouter-utilisateur.echo', methods=['GET','POST'])
# @autorisation_admin
# def ajout_utilisateur():
#    #Un utilisateur
#    form=AjoutUserForm()
#    #Titre de l'onglet
#    title="Ajouter un utilisateur"
#    #Breadcrumb
#    option="Utilisateur"

#    #Envoi de formulaire par la methode POST
#    if form.validate_on_submit():
#       password_user=passwordString()
#       password_hash=bcrypt.generate_password_hash(password_user).decode('utf-8') #génération du password Hacher
#       username_utilisateur=username(form.prenom.data,form.post_nom.data, id_unique()) #Gneration du nom de l'utilsiateur unique
#       #Enregistrement d'un utilisateur
#       user_nv=User(nom=form.nom.data.upper(), post_nom=form.post_nom.data.upper(), prenom=form.prenom.data.capitalize(),\
#       adress=form.adress.data, tel=form.tel.data, username=username_utilisateur, email=form.email.data,\
#       password=password_hash, password_onhash=password_user, droit_id=form.droit_users.data.id)
#       db.session.add(user_nv)
#       db.session.commit()
#       flash("Vous avez enregistré un utilisateur avec droit de ({})".format(form.droit_users.data.nom), "success")
#       return redirect(url_for('user.listeuser'))
      
#    return render_template('user/ajuser.html', form=form, option=option, title=title)

# """ Liste des collaborateurs de la plateforme"""

# @user.route('/liste-utilisateur.echo')
# @login_required
# @autorisation_admin
# def listeuser():
#    #Titre de l'onglet
#    title="Liste des utlisateurs"
#    #Breadcrumb
#    option="Utilisateurs"
#    #Requête d'affichage des utilsiateurs
#    listes=User.query.order_by(User.id.desc())

#    return render_template('user/view.html',title=title, liste=listes, option=option)

# """ Modification du statut de l'utilisateur"""
# @user.route('/statut_user/<int:user_id>')
# @autorisation_admin
# def statut_user(user_id):
#    #Titre
#    title="Statut"
#    #Requête de vérification des sutilisateurs
#    user_statu=User.query.filter_by(id=user_id).first_or_404()

#    #Modification du droit d'accès
#    if user_statu.statut == True:
#       user_statu.statut=False
#       db.session.commit()
#       flash("{} est désactivé sur la plateforme".format(user_statu.prenom),'danger')
#       return redirect(url_for('user.listeuser'))
#    else:
#       user_statu.statut=True
#       db.session.commit()
#       flash("{} est activé sur la plateforme".format(user_statu.prenom),'success')
#       return redirect(url_for('user.listeuser'))
#    return render_template('droit/view.html',title=title)



# """ Profil de l'utilisateur """
# @user.route('/profil-<int:user_id>.echo',methods=('GET', 'POST') )
# @login_required
# def profil(user_id):
#    #Titre
#    title="Profil"
#    #Breadcrumb
#    option="Profil"
#    #Vérification de l'autorisation selon administrateur et collaborateur
#    admin_user(user_id)
#    #Requête de vérification d'utilisateur
#    user_profil=User.query.filter_by(id=user_id).first_or_404()
#    #verfication des articles publié par le collaborateur.
#    publication_pub=Publication.query.filter_by(user_id=user_id).all()
#    #Nombre des publications
#    nbr_pub=[]
#    nbr_pub_actif=[]
#    nbr_pub_non_actif=[]
#    for publication in publication_pub:
#       i=publication.id
#       nbr_pub.insert(0,i)
#       if publication.statut==True:
#          i=publication.id
#          nbr_pub_actif.insert(0,i)
#       else:
#          i=publication.id
#          nbr_pub_non_actif.insert(0,i)
#    #Les variables des publications
#    nbr_pub_plate=int(len(nbr_pub))
#    nbr_pub_plate_ac=int(len(nbr_pub_actif))
#    nbr_pub_plate_non=int(len(nbr_pub_non_actif))
  
#    #Forumulaire des mise à jour de l'tulisateur
#    form=EditerUserForm()

#    if form.validate_on_submit():
#       image_avatar=uplaod_cloudinary_file(form.avatar.data)
#       if image_avatar is None:
#          user_profil.nom=form.nom.data.upper()
#          user_profil.post_nom=form.post_nom.data.upper()
#          user_profil.prenom=form.prenom.data.capitalize()
#          user_profil.adress=form.adress.data
#          user_profil.tel=form.tel.data
#          user_profil.email=form.email.data
#          user_profil.droit_id=form.droit_users.data.id
#          db.session.commit()
#          flash('Modification avec succès',"success")
#          return redirect(url_for('user.listeuser'))
#       else:
#          user_profil.nom=form.nom.data.upper()
#          user_profil.post_nom=form.post_nom.data.upper()
#          user_profil.prenom=form.prenom.data.capitalize()
#          user_profil.adress=form.adress.data
#          user_profil.tel=form.tel.data
#          user_profil.email=form.email.data
#          user_profil.droit_id=form.droit_users.data.id
#          user_profil.avatar=image_avatar
#          db.session.commit()
#          flash('Modification avec succès',"success")
#          return redirect(url_for('user.listeuser'))  
#    #Injection des informations de l'utilisateur dans le formulaire
#    if request.method=='GET':
#       form.nom.data=user_profil.nom
#       form.post_nom.data=user_profil.post_nom
#       form.prenom.data=user_profil.prenom
#       form.adress.data=user_profil.adress
#       form.tel.data=user_profil.tel
#       form.email.data=user_profil.email
#       form.droit_users.data=user_profil.user_droit


   
#    return render_template('user/profil.html',title=title, form=form,option=option, nbr_pub_plate=nbr_pub_plate, nbr_pub_plate_ac=nbr_pub_plate_ac, nbr_pub_plate_non=nbr_pub_plate_non, user_profil=user_profil)


# """ Modification du mot de passe de l'utilisateur """
# @user.route('/motdepasse-<int:user_id>.echo',methods=('GET', 'POST') )
# @login_required
# def password_init(user_id):
#    #Titre
#    title="Initialisation du mot de passe"
#    #Breadcrumb
#    option="Initialisation du mot de passe"
#    #Vérification de l'autorisation selon administrateur et collaborateur
#    admin_user(user_id)
#    #Requête de vérification d'utilisateur
#    user_profil=User.query.filter_by(id=user_id).first_or_404()
#    #Id de l'utilisateur
#    id_user_new=user_id
#    #Formulaire de l'utilisateur
#    form=PassuserForm()
#    #Modification du mot de passe
#    if form.validate_on_submit():
#       print("Gloire")
#       password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8') #génération du password Hacher
#       user_profil.password=password_hash
#       user_profil.password_onhash=form.password.data
#       db.session.commit()
#       #Redirection de l'utilisateur selon l'autorisation
#       if user_profil.id==current_user.id :
#          return redirect(url_for('auth.logout'))
#       else:
#          flash("Mise à jour du mot de passe", 'success')
#          return redirect(url_for('user.profil', user_id=id_user_new))
        
#    return render_template('user/motdepasse.html',title=title, form=form, option=option)

