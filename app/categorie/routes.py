from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Categorie 
from app.categorie.forms import CategorieForm
from flask_login import login_user, current_user, logout_user, login_required

from . import categorie

@categorie.route('/ajouter_categorie')
def ajouter_categorie():
    #Les catagories de livre
    title="Ajouter une catégorie"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=CategorieForm()

    if form.validate_on_submit():
        categorie_ajout=Categorie(nom_categorie=form.nom.data.capitalize())
        db.session.add(categorie_ajout)
        db.session.commit()
        flash('Ajout de la catégorie ({}) avec succès'.format(form.nom.data.capitalize()),'success')
        #return redirect(url_for('categorie.toutes_categorie'))

    return render_template('categorie/ajouterc.html', title=title, form=form)



@categorie.route('/categories')
def index():
    #Les catagories des articles
    title="Liste | Catégorie"
    #Requete de listage des catégories des articles
    list_cate=Categorie.query.all()

    # cat_compte=[]
    # #Nombre des albums
    # for cat in list_cate:
    #     i=album_com.id
    #     album.insert(0,i)
    # nbr_album=len(album)



    return render_template('categorie/index.html', title=title, listes=list_cate)



# @categorie.route('/toutes_categorie')
# @login_required
# def toutes_categorie():

#     #Verification de l'authentification
#     if current_user.admin==False:
#         return redirect(url_for('main.homepage'))

#     #Les catagories de livre
#     title="Les categories"
#      #Liste des rubriques
#     list_cate=Categorie.query.all()
 
#     return render_template('categorie/toutecategories.html', title=title, categories=list_cate)

# #-------------------Statut de la categorie------------------------------

# @categorie.route('/status_categorie/<int:cat_id>')
# @login_required
# def status_categorie(cat_id):

#     #Verification de l'authentification
#     if current_user.admin==False:
#         return redirect(url_for('main.homepage'))

#     #Les catagories de livre
#     title="Les categories"
#     #Verification de l'existence de Rubirque
#     cate_mo=Categorie.query.filter_by(id=cat_id).first_or_404()
#     if cate_mo is None:
#         flash("Veuillez respecté la procedure",'danger')
#         return redirect(url_for('categorie.toutes_categorie'))
#     else:#Changement du statut
#         if cate_mo.status == 1:
#             cate_mo.status = 0
#             db.session.commit()
#             flash("La categorie est désactivée sur la plateforme",'success')
#             return redirect(url_for('categorie.toutes_categorie'))
#         elif cate_mo.status == 0:
#             cate_mo.status = 1
#             db.session.commit()
#             flash("La categorie est activée sur la plateforme",'success')
#             return redirect(url_for('categorie.toutes_categorie'))
#     return render_template('categorie/toutecategories.html', title=title)
# #-----------------------------------------------Editer categorie---------------------

# @categorie.route('/editer_categorie/<int:cat_id>', methods=['GET','POST'])
# @login_required
# def editer_categorie(cat_id):

#     #Verification de l'authentification
#     if current_user.admin==False:
#         return redirect(url_for('main.homepage'))
        
#     #formulaire
#     form=CategorieEditerForm()
#     #Verification de l'existence de Rubirque
#     cate_edit=Categorie.query.filter_by(id=cat_id).first_or_404()
#     #Les catagories de livre
#     title="Modification "+cate_edit.nom
#     #Verification des informations de l'ID
#     if cate_edit is None:
#         flash("Veuillez respecté la procedure",'danger')
#         return redirect(url_for('categorie.toutes_categorie'))
#     #Validation d'enregistrement
#     if form.validate_on_submit():
#         cate_edit.nom=form.nom_ed.data
#         db.session.commit()
#         flash("Modification avec succès",'success')
#         return redirect(url_for('categorie.toutes_categorie'))
#     elif request.method =='GET':
#         form.nom_ed.data=cate_edit.nom

#     return render_template('categorie/modificationcat.html', title=title, form=form)


    