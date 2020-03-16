from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField


from ..models import Fournisseur, Produit, Boutique


def rech_produit():
    return Produit.query.all()

def rech_fournisseur():
    return Fournisseur.query.all()

def rech_boutique():
    return Boutique.query.all()

class StockageForm(FlaskForm):
    quantite= IntegerField('quantité', validators=[DataRequired("Completer la quantité")])
    prix_d= DecimalField('prix')
    date_op= StringField('Date', validators=[DataRequired("Completer la date")])
    produit_stock= QuerySelectField(query_factory=rech_produit, get_label='nom_produit', allow_blank=False)
    fournissseur_stock= QuerySelectField(query_factory=rech_fournisseur, get_label='nom_fourn', allow_blank=False)

    submit = SubmitField('Stock produit')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_prix_d(self, prix_d):
        prix_dachat=prix_d.data
        if prix_dachat < 0:
            raise ValidationError("Le prix d'achat doit être superieure à Zero")
    
    def validate_quantite(self, quantite):
        quantite_o=quantite.data
        if quantite_o < 0:
            raise ValidationError("Quantité doit être superieure à Zero")


class StockageErreurForm(FlaskForm):
    quantite= IntegerField('quantité', validators=[DataRequired("Completer la quantité")])
    prix_d= DecimalField('prix')
    date_op= StringField('Date', validators=[DataRequired("Completer la date")])
    produit_stock= QuerySelectField(query_factory=rech_produit, get_label='nom_produit', allow_blank=False)


    submit = SubmitField('Erreur Stockage')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_prix_d(self, prix_d):
        prix_dachat=prix_d.data
        if prix_dachat < 0:
            raise ValidationError("Le prix d'achat doit être superieure à Zero")
    
    def validate_quantite(self, quantite):
        quantite_o=quantite.data
        if quantite_o < 0:
            raise ValidationError("Quantité doit être superieure à Zero")

class BoutiqueRechForm(FlaskForm):
    quantite= IntegerField('quantité', validators=[DataRequired("Completer la quantité")])
    prix_d= DecimalField('prix')
    date_op= StringField('Date', validators=[DataRequired("Completer la date")])
    boutiques_cherch= QuerySelectField(query_factory=rech_boutique, get_label='nom_boutique', allow_blank=False)
    produit_stock= QuerySelectField(query_factory=rech_produit, get_label='nom_produit', allow_blank=False)


    submit = SubmitField('Tranfert boutique')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_prix_d(self, prix_d):
        prix_dachat=prix_d.data
        if prix_dachat < 0:
            raise ValidationError("Le prix d'achat doit être superieure à Zero")
    
    def validate_quantite(self, quantite):
        quantite_o=quantite.data
        if quantite_o < 0:
            raise ValidationError("Quantité doit être superieure à Zero")





# class EditUserForm(FlaskForm):
#     nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
#     post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
#     prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
#     adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
#     tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=13, message="Veuillez respecté les caractères")])
#     email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
#     boutique_users= QuerySelectField(query_factory=rech_boutique, get_label='nom_boutique', allow_blank=False)
#     avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])
#     role= SelectField('Rôle',choices=[('Gérant', 'Gérant'), ('Magasinier', 'Magasinier'), ('Vendeur', 'Vendeur'), ('Associé', 'Associé') ])
#     depot_users= QuerySelectField(query_factory=rech_depot, get_label='nom_depot', allow_blank=False)

#     submit = SubmitField('Ajouter user')

# class PassuserForm(FlaskForm):
#     password= PasswordField('Mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe')])
#     confirm_password= PasswordField('Confirmer mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe'), EqualTo('password',message="Les mots des passes ne pas conforment")])
#     submit = SubmitField('Changer mot de passe')

