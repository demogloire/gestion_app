from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Categorie, Produit, Depot
from app.depot.forms import DepotForm, DepotEditForm
from flask_login import login_user, current_user, logout_user, login_required

from . import depot

@depot.route('/ajouter_depot', methods=['GET','POST'])
def ajouterdepot():
    #Les dépots
    title="Ajouter un dépôt"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=DepotForm()

    if form.validate_on_submit():
        depot=Depot(nom_depot=form.nom_depot.data.capitalize())
        db.session.add(depot)
        db.session.commit()
        flash('Vous avez ajouté ({}) comme dépôt'.format(form.nom_depot.data.capitalize()),'success')
        return redirect(url_for('depot.index'))

    return render_template('depot/ajouterc.html', title=title, form=form)



@depot.route('/')
def index():

    title="Liste | dépôt"
    #Requete de listage des dépôts
    list_depot=Depot.query.all()

    return render_template('depot/index.html', title=title, listes=list_depot)


@depot.route('/<int:dep_id>/depot', methods=['GET','POST'])
#@login_required
def editer_depot(dep_id):

    # #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))
        
    #formulaire
    form=DepotEditForm()
    #Verification de l'existence de dépôt
    dep_edit=Depot.query.filter_by(id=dep_id).first_or_404()
    #Titre de la catégorie
    title=" {} | Modification "+dep_edit.nom_depot

    #Validation d'enregistrement
    if form.validate_on_submit():
        dep_edit.nom_depot=form.nom_depot.data.capitalize()
        db.session.commit()
        flash("Modification avec succès",'success')
        return redirect(url_for('depot.index'))
    elif request.method =='GET':
        form.nom_depot.data=dep_edit.nom_depot

    return render_template('depot/depotedit.html', title=title, form=form)


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


    