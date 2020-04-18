from flask_wtf import FlaskForm
import re
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
    date_op= StringField('Date', validators=[DataRequired("Completer la date"),  Length(min=10, max=200, message="Format 02-02-2020")])
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
    date_op= StringField('Date', validators=[DataRequired("Completer la date"), Length(min=10, max=200, message="Format 02-02-2020")])
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
    date_op= StringField('Date', validators=[DataRequired("Completer la date"),  Length(min=10, max=200, message="Format 02-02-2020")])
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


class AnneeTransForm(FlaskForm):
    date_annee_recherche= StringField("Date", validators=[DataRequired("La date svp"), Length(min=10, max=200, message="Format 02-02-2020")])
    boutiques_cherch= QuerySelectField(query_factory=rech_boutique, get_label='nom_boutique', allow_blank=True)
    produit_stock= QuerySelectField(query_factory=rech_produit, get_label='nom_produit', allow_blank=True)
    submit_rap = SubmitField('Chercher')

    def validate_boutiques_cherch(self, boutiques_cherch):
        d=boutiques_cherch.data
        if d is None:
            boutiques_cherch.data=0

    def validate_produit_stock(self, produit_stock):
        d=produit_stock.data
        if d is None:
            produit_stock.data=0

    def validate_date_annee_recherche(self, date_annee_recherche):
        date=date_annee_recherche.data
        result = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", date)
        if result:
            pass
        else:
            raise ValidationError("La date doit respectée cette format jj-mm-aaaa")


class MensuelTransForm(FlaskForm):
    date_annee_recherche= StringField("Date", validators=[DataRequired("La date svp"), Length(min=10, max=200, message="Format 02-02-2020")])
    produit_stock= QuerySelectField(query_factory=rech_produit, get_label='nom_produit', allow_blank=True)
    submit_rap = SubmitField('Chercher')

    def validate_boutiques_cherch(self, boutiques_cherch):
        d=boutiques_cherch.data
        if d is None:
            boutiques_cherch.data=0

    def validate_produit_stock(self, produit_stock):
        d=produit_stock.data
        if d is None:
            produit_stock.data=0

    def validate_date_annee_recherche(self, date_annee_recherche):
        date=date_annee_recherche.data
        result = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", date)
        if result:
            pass
        else:
            raise ValidationError("La date doit respectée cette format jj-mm-aaaa")

