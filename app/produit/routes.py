from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Produit, Categorie 
from app.produit.forms import ProduitJForm, ProduitAForm
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
        #Les informations de données de la catégorie
        categorie_id=form.categorie.data.id
        nombre_de_article_assoc=form.categorie.data.articles_associ # Nombre d'article associé
        code_produit="{}{}".format(codeproduit(),categorie_id) #Code produit total

        #Vérification des informations sur les emballages        
        if form.emballage.data == "Box" or form.emballage.data == "Carton":
            nbr_contenu=int(form.nombre_contenu.data)
            if nbr_contenu < 2 :
                flash("Le nombre des élements du {} doit être supieur à 1 ".format(form.emballage.data),'danger')
                return redirect(url_for('produit.ajouterproduit'))
        
        #Les informations de la catégorie
        cat_assoc=Categorie.query.filter_by(id=categorie_id).first() #Récuperation des informations de la catégorie
        cat_assoc.articles_associ=nombre_de_article_assoc+1
        db.session.commit()

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


@produit.route('/produit/<string:code_pro>', methods=['GET','POST'])
def mod_pro(code_pro):
    #Les catagories de livre
    title="Modifification | Lambda Gestion"

    #Verification de l'authentification
    # if current_user.admin==False:
    #     return redirect(url_for('main.homepage'))

    #Declaration du formulaire
    form=ProduitAForm()
    #Produit à modifier
    produit_mod=Produit.query.filter_by(code_produit=code_pro).first_or_404()

    if form.validate_on_submit():
        #Les informations de données de la catégorie
        categorie_id=form.categorie.data.id
        nombre_de_article_assoc=form.categorie.data.articles_associ # Nombre d'article associé
        #Vérification des informations sur les emballages        
        if form.emballage.data == "Box" or form.emballage.data == "Carton":
            nbr_contenu=int(form.nombre_contenu.data)
            if nbr_contenu < 2 :
                flash("Le nombre des élements du {} doit être supieur à 1 ".format(form.emballage.data),'danger')
                return redirect(url_for('produit.ajouterproduit'))
        
        #Les informations de la catégorie
        if categorie_id != produit_mod.categorie_id:
            cat_assoc=Categorie.query.filter_by(id=categorie_id).first() #Récuperation des informations de la catégorie
            cat_assoc.articles_associ=nombre_de_article_assoc+1
            db.session.commit()

        #Vérification de l'image upload sur le produit
        if form.avatar.data:
            avatar_produit= save_picture(form.avatar.data) #reduction de la taille de l'image
            produit_mod.nom_produit=form.nom_produit.data.capitalize()
            produit_mod.description=form.description.data
            produit_mod.prix_achat=form.prix_achat.data
            produit_mod.prix_vente=form.prix_vente.data
            produit_mod.prix_achat_g=form.prix_achat_g.data
            produit_mod.prix_vente_g=form.prix_vente_g.data
            produit_mod.avatar=avatar_produit
            produit_mod.emballage=form.emballage.data
            produit_mod.nombre_contenu=form.nombre_contenu.data
            produit_mod.categorie_id=categorie_id
            db.session.commit()
            flash("Modification de ({}) avec succès".format(form.nom_produit.data.capitalize()),'success')
            return redirect(url_for('produit.index'))
        else:
            produit_mod.nom_produit=form.nom_produit.data.capitalize()
            produit_mod.description=form.description.data
            produit_mod.prix_achat=form.prix_achat.data
            produit_mod.prix_vente=form.prix_vente.data
            produit_mod.prix_achat_g=form.prix_achat_g.data
            produit_mod.prix_vente_g=form.prix_vente_g.data
            produit_mod.emballage=form.emballage.data
            produit_mod.nombre_contenu=form.nombre_contenu.data
            produit_mod.categorie_id=categorie_id
            db.session.commit()
            flash("Modification de ({}) avec succès".format(form.nom_produit.data.capitalize()),'success')
            return redirect(url_for('produit.index'))
    if request.method=="GET":
        form.nom_produit.data=produit_mod.nom_produit
        form.description.data=produit_mod.description
        form.prix_achat.data=produit_mod.prix_achat
        form.prix_vente.data=produit_mod.prix_vente
        form.prix_achat_g.data=produit_mod.prix_achat_g
        form.prix_vente_g.data=produit_mod.prix_vente_g
        form.emballage.data=produit_mod.emballage
        form.nombre_contenu.data=produit_mod.nombre_contenu
        form.categorie.data=produit_mod.produit_categorie
        

    return render_template('produit/modpro.html', title=title, form=form)


@produit.route('/')
def index():
    #Les produits 
    title="Produits | Lambda Gestion"
    #Requet des pagination et des listage des données
    page= request.args.get('page', 1, type=int)
    produit_page=Produit.query.order_by(Produit.id.desc()).paginate(page=page, per_page=21)

    return render_template('produit/index.html', title=title, listes=produit_page)


