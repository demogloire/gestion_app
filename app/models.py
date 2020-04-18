from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin, current_user   
from sqlalchemy.orm import backref

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_produit = db.Column(db.String(128))
    nom_produit = db.Column(db.String(128))
    description = db.Column(db.Text)
    vt_gros_piece = db.Column(db.DECIMAL(precision=20, scale=16))
    vt_detaille_piece = db.Column(db.DECIMAL(precision=20, scale=16))
    vt_gros_entier = db.Column(db.DECIMAL(precision=20, scale=16))
    cout_d_achat = db.Column(db.DECIMAL(precision=20, scale=16))
    avatar = db.Column(db.String(128), default="avatar.jpg")
    emballage = db.Column(db.String(128))
    nombre_contenu=db.Column(db.Integer, default=1)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=False)
    stocks = db.relationship('Stock', backref='stock_produit', lazy='dynamic')
    produitboutiques = db.relationship('Produitboutique', backref='produitboutique_produit', lazy='dynamic')

class Categorie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_categorie = db.Column(db.String(128))
    produits = db.relationship('Produit', backref='produit_categorie', lazy='dynamic')
    articles_associ=db.Column(db.Integer, default=0)
    produitboutiques = db.relationship('Produitboutique', backref='produitboutique_categorie', lazy='dynamic')
    
class Fournisseur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fourn = db.Column(db.String(128))
    tel_fourn = db.Column(db.String(128))
    email = db.Column(db.String(128))
    adresse = db.Column(db.String(128))
    stocks = db.relationship('Stock', backref='stock_fournisseur', lazy='dynamic')

class Typecommande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commande = db.Column(db.String(128))
    date_commande = db.Column(db.Date)
    valeur = db.Column(db.DECIMAL(precision=20, scale=16))
    commandes = db.relationship('Commande', backref='commande_typecommande', lazy='dynamic')

class Typeclient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_type = db.Column(db.Text)
    statut = db.Column(db.Boolean, default=False) 
    clients = db.relationship('Client', backref='client_typeclient', lazy='dynamic')

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantite = db.Column(db.Integer)
    valeur = db.Column(db.DECIMAL(precision=20, scale=16))
    datest = db.Column(db.Date)
    prix_unit = db.Column(db.DECIMAL(precision=20, scale=16))
    disponible = db.Column(db.Integer, default=0)
    valeur_dispo = db.Column(db.DECIMAL(precision=20, scale=16), default=0)
    stockage = db.Column(db.Boolean, default=False)
    transfert = db.Column(db.Boolean, default=False)
    erreur = db.Column(db.Boolean, default=False)
    facture_annule = db.Column(db.Boolean, default=False)
    vente_boutique = db.Column(db.Boolean, default=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'))
    depot_id = db.Column(db.Integer, db.ForeignKey('depot.id'))
    boutique_id = db.Column(db.Integer, db.ForeignKey('boutique.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fournisseur_id = db.Column(db.Integer, db.ForeignKey('fournisseur.id'))
    produitboutique_id = db.Column(db.Integer, db.ForeignKey('produitboutique.id'))
    solde = db.Column(db.Boolean, default=False)


class Depot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_depot = db.Column(db.String(128))
    stocks = db.relationship('Stock', backref='stock_depot', lazy='dynamic')
    users = db.relationship('User', backref='user_depot', lazy='dynamic')


class Boutique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_boutique = db.Column(db.String(128))
    factures = db.relationship('Facture', backref='facture_boutique', lazy='dynamic')
    produitboutiques = db.relationship('Produitboutique', backref='produitboutique_boutique', lazy='dynamic')
    comptedepenses = db.relationship('Comptedepense', backref='comptedepense_boutique', lazy='dynamic')
    clients = db.relationship('Client', backref='client_boutique', lazy='dynamic')
    users = db.relationship('User', backref='user_boutique', lazy='dynamic')
    stocks = db.relationship('Stock', backref='stock_boutique', lazy='dynamic')

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_client = db.Column(db.String(128))
    tel_client = db.Column(db.String(128))
    email = db.Column(db.String(128))
    adresse = db.Column(db.String(128))
    factures = db.relationship('Facture', backref='facture_client', lazy='dynamic')
    typeclient_id = db.Column(db.Integer, db.ForeignKey('typeclient.id'), nullable=False)
    boutique_id = db.Column(db.Integer, db.ForeignKey('boutique.id'), nullable=False)

class Produitboutique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_produit = db.Column(db.String(128))
    nom_produit = db.Column(db.String(128))
    description = db.Column(db.Text)
    vt_gros_piece = db.Column(db.DECIMAL(precision=20, scale=16))
    vt_detaille_piece = db.Column(db.DECIMAL(precision=20, scale=16))
    vt_gros_entier = db.Column(db.DECIMAL(precision=20, scale=16))
    cout_d_achat = db.Column(db.DECIMAL(precision=20, scale=16))
    avatar = db.Column(db.String(128), default="avatar.jpg")
    emballage = db.Column(db.String(128))
    nombre_contenu=db.Column(db.Integer, default=1)
    stocks = db.relationship('Stock', backref='stock_produitboutique', lazy='dynamic')
    boutique_id = db.Column(db.Integer, db.ForeignKey('boutique.id'), nullable=False)
    categorie_id = db.Column(db.Integer, db.ForeignKey('categorie.id'), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey('produit.id'), nullable=False)
    ventes = db.relationship('Vente', backref='vente_produitboutique', lazy='dynamic')

class Commande(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantite_commande = db.Column(db.Integer)
    prix_unitaire = db.Column(db.DECIMAL(precision=20, scale=16))
    date = db.Column(db.Date)
    typecomande_id = db.Column(db.Integer, db.ForeignKey('typecommande.id'), nullable=False)

class Vente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantite = db.Column(db.DECIMAL(precision=20, scale=16))
    montant = db.Column(db.DECIMAL(precision=20, scale=16))
    prix_unitaire = db.Column(db.DECIMAL(precision=20, scale=16))
    no_facture = db.Column(db.Boolean, default=False)
    facture_id = db.Column(db.Integer, db.ForeignKey('facture.id'), nullable=False)
    produitboutique_id = db.Column(db.Integer, db.ForeignKey('produitboutique.id'), nullable=False)

class Facture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_facture = db.Column(db.String(128))
    montant = db.Column(db.DECIMAL(precision=20, scale=16), default=0)
    cash = db.Column(db.Boolean, default=False)
    dette = db.Column(db.Boolean, default=False)
    annule = db.Column(db.Boolean, default=False)
    vente_acompte = db.Column(db.Boolean, default=False)
    type_vente = db.Column(db.Boolean, default=False)
    liquidation = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date)
    code_id_facture= db.Column(db.Integer)
    valide_account = db.Column(db.Boolean, default=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    boutique_id = db.Column(db.Integer, db.ForeignKey('boutique.id'), nullable=False)
    ventes = db.relationship('Vente', backref='vente_facture', lazy='dynamic')
    payements = db.relationship('Payement', backref='payement_facture', lazy='dynamic')


class Achat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    date = db.Column(db.Date)
    type_achat = db.Column(db.String(128))
    fraisconnexes = db.relationship('Fraisconnexe', backref='fraisconnexe_achat', lazy='dynamic')

class Fraisconnexe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frais = db.Column(db.DECIMAL(precision=20, scale=16))
    montant = db.Column(db.DECIMAL(precision=20, scale=16))
    achat_id = db.Column(db.Integer, db.ForeignKey('achat.id'), nullable=False)

class Comptedepense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rubrique = db.Column(db.String(128))
    boutique_id = db.Column(db.Integer, db.ForeignKey('boutique.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    depenses = db.relationship('Depense', backref='depense_comptedepense', lazy='dynamic')

class Depense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    montant = db.Column(db.DECIMAL(precision=20, scale=16))
    date = db.Column(db.Date)
    comptedepense_id = db.Column(db.Integer, db.ForeignKey('comptedepense.id'), nullable=False)

class Operation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    motif = db.Column(db.Text)
    montant = db.Column(db.DECIMAL(precision=20, scale=16))
    compte_id = db.Column(db.Integer, db.ForeignKey('comptes.id'), nullable=False)

class Comptes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compte = db.Column(db.String(128))
    operations = db.relationship('Operation', backref='operation_compte', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(128))
    post_nom = db.Column(db.String(128))
    prenom= db.Column(db.String(128))
    adress = db.Column(db.String(128))
    tel = db.Column(db.String(128))
    email = db.Column(db.String(128))
    password = db.Column(db.String(128))
    password_onhash = db.Column(db.String(128))
    statut=db.Column(db.Boolean, default=False)
    avatar=db.Column(db.String(128), default='user.png')
    role = db.Column(db.String(128))
    depot_id = db.Column(db.Integer, db.ForeignKey('depot.id'))
    entreprise_id = db.Column(db.Integer, db.ForeignKey('entreprise.id'))
    boutique_id = db.Column(db.Integer, db.ForeignKey('boutique.id'))
    comptes = db.relationship('Comptes', backref='compte_user', lazy='dynamic')
    comptedepenses = db.relationship('Comptedepense', backref='comptedepense_user', lazy='dynamic')
    factures = db.relationship('Facture', backref='facture_user', lazy='dynamic')
    stocks = db.relationship('Stock', backref='stock_user', lazy='dynamic')

class Entreprise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    denomination = db.Column(db.String(128))
    personalite = db.Column(db.String(255))
    adresse=db.Column(db.String(255))
    siege_social=db.Column(db.String(125))
    telephone=db.Column(db.String(20))
    email=db.Column(db.String(125))
    fax=db.Column(db.String(125))
    avatar = db.Column(db.String(128), default="logo.jpg")
    users = db.relationship('User', backref='user_entreprise', lazy='dynamic')


class Payement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code_payement = db.Column(db.String(128))
    denomination = db.Column(db.String(128))
    montant = db.Column(db.DECIMAL(precision=20, scale=16), default=0)
    liquidation = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date)
    facture_id = db.Column(db.Integer, db.ForeignKey('facture.id'), nullable=False)



    
    


