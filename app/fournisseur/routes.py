from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Fournisseur
from app.fournisseur.forms import FournisseurForm, CategorieEditerForm
from flask_login import login_user, current_user, logout_user, login_required

from . import fournisseur

@fournisseur.route('/ajouter_fournisseur', methods=['GET','POST'])
def ajouterfounisseur():
    #Les catagories de livre
    title="Fournisseur | Lambda Gestion"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=FournisseurForm()

    if form.validate_on_submit():
        categorie_ajout=Categorie(nom_categorie=form.nom.data.capitalize())
        db.session.add(categorie_ajout)
        db.session.commit()
        flash('Ajout de la catégorie ({}) avec succès'.format(form.nom.data.capitalize()),'success')
        return redirect(url_for('categorie.index'))
    return render_template('fournisseur/ajouterf.html', title=title, form=form)



# @categorie.route('/categories')
# def index():
#     #Les catagories des articles
#     title="Liste | Catégorie"
#     #Requete de listage des catégories des articles
#     list_cate=Categorie.query.all()

#     return render_template('categorie/index.html', title=title, listes=list_cate)





# @categorie.route('/<int:cat_id>/categorie', methods=['GET','POST'])
# #@login_required
# def editer_categorie(cat_id):

#     # #Verification de l'authentification
#     # if current_user.admin==False:
#     #     return redirect(url_for('main.homepage'))
        
#     #formulaire
#     form=CategorieEditerForm()
#     #Verification de l'existence de la cetégorie
#     cate_edit=Categorie.query.filter_by(id=cat_id).first_or_404()
#     #Titre de la catégorie
#     title=" {} | Modification "+cate_edit.nom_categorie
#     #Verification des informations de l'ID
#     if cate_edit is None:
#         flash("Veuillez respecté la procedure",'danger')
#         return redirect(url_for('categorie.index'))
#     #Validation d'enregistrement
#     if form.validate_on_submit():
#         cate_edit.nom_categorie=form.nom.data
#         db.session.commit()
#         flash("Modification avec succès",'success')
#         return redirect(url_for('categorie.index'))
#     elif request.method =='GET':
#         form.nom.data=cate_edit.nom_categorie

#     return render_template('categorie/categoriemodif.html', title=title, form=form)


# @categorie.route('/<int:cat_id>/association', methods=['GET','POST'])
# #@login_required
# def association_categorie(cat_id):

#     # #Verification de l'authentification
#     # if current_user.admin==False:
#     #     return redirect(url_for('main.homepage'))
    
#     #Verification de l'existence de la cetégorie
#     cate_association=Categorie.query.filter_by(id=cat_id).first_or_404()
#     #Titre de la catégorie
#     title=" {} | Association "+cate_association.nom_categorie
#     #Verification des informations de l'ID
#     if cate_association is None:
#         flash("Veuillez respecté la procedure",'danger')
#         return redirect(url_for('categorie.index'))
#     #Vérification des produit associé à la catégorie.
#     produits=Produit.query.filter_by(categorie_id=cat_id)
#     #Nom de la catégorie de l'association.
#     nom_categorie_association=cate_association.nom_categorie
    
#     return render_template('categorie/catassocie.html', nom_categorie_association=nom_categorie_association, title=title, produits=produits)


    