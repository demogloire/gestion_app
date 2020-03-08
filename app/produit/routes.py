from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Produit 
from app.produit.forms import ProduitJForm
from app.utility.utility import save_picture, codeproduit
from flask_login import login_user, current_user, logout_user, login_required

from . import produit

@produit.route('/ajouter_produit', methods=['GET','POST'])
def ajouterproduit():
    #Les catagories de livre
    title="Ajouter un produit"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=ProduitJForm()

    if form.validate_on_submit():
        categorie_id=form.categorie.data.id
        code_produit="{}{}".format(codeproduit(),categorie_id) #Code produit total
        #Vérification des informations sur les emballages        
        if form.emballage.data == "Box" or form.emballage.data == "Carton":
            nbr_contenu=int(form.nombre_contenu.data)
            if nbr_contenu < 2 :
                flash("Le nombre des élements du {} doit être supieur à 1 ".format(form.emballage.data),'danger')
                return redirect(url_for('produit.ajouterproduit'))
        #Vérification de l'image upload sur le produit
        if form.avatar.data:
            avatar_produit= save_picture(form.avatar.data) #reduction de la taille de l'image
            produit=Produit(code_produit=code_produit, nom_produit=form.nom_produit.data.capitalize(), description=form.description.data,
                            prix_achat=form.prix_achat.data, prix_vente=form.prix_vente.data, prix_achat_g=form.prix_achat_g.data, 
                            prix_vente_g=form.prix_vente_g.data, avatar=avatar_produit, emballage=form.emballage.data,nombre_contenu=form.nombre_contenu.data, 
                            categorie_id=categorie_id)
            db.session.add(produit)
            db.session.commit()
            flash("Ajout d'un produit ({}) avec succès".format(form.nom_produit.data.capitalize()),'success')
            #return redirect(url_for('categorie.index'))
        else:
            produit=Produit(code_produit=code_produit, nom_produit=form.nom_produit.data.capitalize(), description=form.description.data,
                            prix_achat=form.prix_achat.data, prix_achat_g=form.prix_achat_g.data, prix_vente_g=form.prix_vente_g.data, prix_vente=form.prix_vente.data, 
                            emballage=form.emballage.data,nombre_contenu=form.nombre_contenu.data, categorie_id=categorie_id)

            db.session.add(produit)
            db.session.commit()
            flash("Ajout d'un produit ({}) avec succès".format(form.nom_produit.data.capitalize()),'success')

    return render_template('produit/ajouterp.html', title=title, form=form)



# @categorie.route('/categories')
# def index():
#     #Les catagories des articles
#     title="Liste | Catégorie"
#     #Requete de listage des catégories des articles
#     list_cate=Categorie.query.all()

#     return render_template('categorie/index.html', title=title, listes=list_cate)



# # @categorie.route('/toutes_categorie')
# # @login_required
# # def toutes_categorie():

# #     #Verification de l'authentification
# #     if current_user.admin==False:
# #         return redirect(url_for('main.homepage'))

# #     #Les catagories de livre
# #     title="Les categories"
# #      #Liste des rubriques
# #     list_cate=Categorie.query.all()
 
# #     return render_template('categorie/toutecategories.html', title=title, categories=list_cate)

# # #-------------------Statut de la categorie------------------------------

# # @categorie.route('/status_categorie/<int:cat_id>')
# # @login_required
# # def status_categorie(cat_id):

# #     #Verification de l'authentification
# #     if current_user.admin==False:
# #         return redirect(url_for('main.homepage'))

# #     #Les catagories de livre
# #     title="Les categories"
# #     #Verification de l'existence de Rubirque
# #     cate_mo=Categorie.query.filter_by(id=cat_id).first_or_404()
# #     if cate_mo is None:
# #         flash("Veuillez respecté la procedure",'danger')
# #         return redirect(url_for('categorie.toutes_categorie'))
# #     else:#Changement du statut
# #         if cate_mo.status == 1:
# #             cate_mo.status = 0
# #             db.session.commit()
# #             flash("La categorie est désactivée sur la plateforme",'success')
# #             return redirect(url_for('categorie.toutes_categorie'))
# #         elif cate_mo.status == 0:
# #             cate_mo.status = 1
# #             db.session.commit()
# #             flash("La categorie est activée sur la plateforme",'success')
# #             return redirect(url_for('categorie.toutes_categorie'))
# #     return render_template('categorie/toutecategories.html', title=title)
# # #-----------------------------------------------Editer categorie---------------------

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


    