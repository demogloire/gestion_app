from flask import render_template, flash, url_for, redirect, request
from .. import db
from ..models import Produit, Categorie, Produitboutique
from app.produit.forms import ProduitJForm, ProduitAForm
import app.pack_fonction.fonction as utilitaire
from app.produit.autorisation  import autorisation_gerant
#from app.pack_fonction.fonction import save_picture, codeproduit
from flask_login import login_user, current_user, logout_user, login_required

from . import produit

@produit.route('/ajouter_produit', methods=['GET','POST'])
@login_required
@autorisation_gerant
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
        code_produit="{}{}".format(utilitaire.codeproduit(),categorie_id) #Code produit total

        #Vérification des informations sur les emballages        
        if form.emballage.data == "Box" or form.emballage.data == "Carton":
            nbr_contenu=int(form.nombre_contenu.data)
            if nbr_contenu < 2 :
                flash("Le nombre des élements du {} doit être supieur à 1 Pièce ".format(form.emballage.data),'danger')
                return redirect(url_for('produit.ajouterproduit'))
            
        
        #Les informations de la catégorie
        cat_assoc=Categorie.query.filter_by(id=categorie_id).first() #Récuperation des informations de la catégorie
        cat_assoc.articles_associ=nombre_de_article_assoc+1
        db.session.commit()

        # Le contenu de l'emballage
        contenu_article=None
        if form.emballage.data == "Vrac" or form.emballage.data=="Sac":
            contenu_article=1
        else:
            contenu_article=form.nombre_contenu.data

        #Vérification de l'image upload sur le produit
        if form.avatar.data:
            avatar_produit= utilitaire.save_picture_produit(form.avatar.data) #reduction de la taille de l'image
            produit=Produit(code_produit=code_produit, nom_produit=form.nom_produit.data.capitalize(), description=form.description.data,
                            vt_gros_piece=form.vt_gros_piece.data, vt_detaille_piece=form.vt_detaille_piece.data, vt_gros_entier=form.vt_gros_entier.data, 
                            cout_d_achat=form.cout_d_achat.data, avatar=avatar_produit, emballage=form.emballage.data,nombre_contenu=contenu_article, 
                            categorie_id=categorie_id)
            db.session.add(produit)
            db.session.commit()
            flash("Ajout d'un produit ({}) avec succès".format(form.nom_produit.data.capitalize()),'success')
            return redirect(url_for('produit.index'))
        else:
            produit=Produit(code_produit=code_produit, nom_produit=form.nom_produit.data.capitalize(), description=form.description.data,
                            vt_gros_piece=form.vt_gros_piece.data, vt_detaille_piece=form.vt_detaille_piece.data, vt_gros_entier=form.vt_gros_entier.data, 
                            cout_d_achat=form.cout_d_achat.data, emballage=form.emballage.data,nombre_contenu=contenu_article, 
                            categorie_id=categorie_id)
            db.session.add(produit)
            db.session.commit()
            flash("Ajout d'un produit ({}) avec succès".format(form.nom_produit.data.capitalize()),'success')
            return redirect(url_for('produit.index'))
        
    return render_template('produit/ajouterp.html', title=title, form=form)


@produit.route('/produit/<string:code_pro>', methods=['GET','POST'])
@login_required
@autorisation_gerant
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
    #Produit aux boutique
    produit_mod_boutique=Produitboutique.query.filter_by(produit_id=produit_mod.id).all()
    liste_vide_boutqiue=[]

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
        
        # Le contenu de l'emballage
        contenu_article=None
        if form.emballage.data == "Vrac" or form.emballage.data=="Sac":
            contenu_article=1
        else:
            contenu_article=form.nombre_contenu.data

        #Vérification de l'image upload sur le produit
        if form.avatar.data:
            avatar_produit= utilitaire.save_picture_produit(form.avatar.data) #reduction de la taille de l'image
            produit_mod.nom_produit=form.nom_produit.data.capitalize()
            produit_mod.description=form.description.data
            produit_mod.vt_gros_piece=form.vt_gros_piece.data
            produit_mod.vt_detaille_piece=form.vt_detaille_piece.data
            produit_mod.vt_gros_entier=form.vt_gros_entier.data
            produit_mod.cout_d_achat=form.cout_d_achat.data
            produit_mod.avatar=avatar_produit
            produit_mod.emballage=form.emballage.data
            produit_mod.nombre_contenu=contenu_article
            produit_mod.categorie_id=categorie_id
            #Mise à jour de produit de la boutique
            if liste_vide_boutqiue != produit_mod_boutique:
                for maj_pro_boutique in produit_mod_boutique:
                    maj_pro_boutique.nom_produit=form.nom_produit.data.capitalize()
                    maj_pro_boutique.description=form.description.data
                    maj_pro_boutique.vt_gros_piece=form.vt_gros_piece.data
                    maj_pro_boutique.vt_detaille_piece=form.vt_detaille_piece.data
                    maj_pro_boutique.vt_gros_entier=form.vt_gros_entier.data
                    maj_pro_boutique.cout_d_achat=form.cout_d_achat.data
                    maj_pro_boutique.avatar=avatar_produit
                    maj_pro_boutique.emballage=form.emballage.data
                    maj_pro_boutique.nombre_contenu=contenu_article
                    maj_pro_boutique.categorie_id=categorie_id
            db.session.commit()
            flash("Modification de ({}) des boutiques et aux dépots avec succès ".format(form.nom_produit.data.capitalize()),'success')
            return redirect(url_for('produit.index'))
        else:
            produit_mod.nom_produit=form.nom_produit.data.capitalize()
            produit_mod.description=form.description.data
            produit_mod.vt_gros_piece=form.vt_gros_piece.data
            produit_mod.vt_detaille_piece=form.vt_detaille_piece.data
            produit_mod.vt_gros_entier=form.vt_gros_entier.data
            produit_mod.cout_d_achat=form.cout_d_achat.data
            produit_mod.emballage=form.emballage.data
            produit_mod.nombre_contenu=contenu_article
            produit_mod.categorie_id=categorie_id
            #Mise à jour de produit de la boutique
            if liste_vide_boutqiue != liste_vide_boutqiue:
                for maj_pro_boutique in produit_mod_boutique:
                    maj_pro_boutique.nom_produit=form.nom_produit.data.capitalize()
                    maj_pro_boutique.description=form.description.data
                    maj_pro_boutique.vt_gros_piece=form.vt_gros_piece.data
                    maj_pro_boutique.vt_detaille_piece=form.vt_detaille_piece.data
                    maj_pro_boutique.vt_gros_entier=form.vt_gros_entier.data
                    maj_pro_boutique.cout_d_achat=form.cout_d_achat.data
                    maj_pro_boutique.avatar=avatar_produit
                    maj_pro_boutique.emballage=form.emballage.data
                    maj_pro_boutique.nombre_contenu=contenu_article
                    maj_pro_boutique.categorie_id=categorie_id
            db.session.commit()
            flash("Modification de ({}) des boutiques et aux dépots avec succès ".format(form.nom_produit.data.capitalize()),'success')
            return redirect(url_for('produit.index'))
    if request.method=="GET":
        form.nom_produit.data=produit_mod.nom_produit
        form.description.data=produit_mod.description
        form.vt_gros_piece.data=produit_mod.vt_gros_piece
        form.vt_detaille_piece.data=produit_mod.vt_detaille_piece
        form.vt_gros_entier.data=produit_mod.vt_gros_entier
        form.cout_d_achat.data=produit_mod.cout_d_achat
        form.emballage.data=produit_mod.emballage
        form.nombre_contenu.data=produit_mod.nombre_contenu
        form.categorie.data=produit_mod.produit_categorie
    return render_template('produit/modpro.html', title=title, form=form)


@produit.route('/')
@login_required
@autorisation_gerant
def index():
    #Les produits 
    title="Produits | {} ".format(current_user.user_entreprise.denomination)
    #Requet des pagination et des listage des données
    page= request.args.get('page', 1, type=int)
    produit_page=Produit.query.order_by(Produit.id.desc()).paginate(page=page, per_page=21)

    return render_template('produit/index.html', title=title, listes=produit_page)


