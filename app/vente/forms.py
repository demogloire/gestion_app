from flask_wtf import FlaskForm
import re
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import login_user, current_user, login_required


from ..models import Fournisseur, Produit, Boutique, Client, Produitboutique, Facture


def rech_produit():
    return Produit.query.all()

def rech_fournisseur():
    return Fournisseur.query.all()

def rech_boutique():
    return Boutique.query.all()

def rech_client():
    return Client.query.filter_by(boutique_id=current_user.boutique_id).all()

def rech_produit_boutique():
    return Produitboutique.query.filter_by(boutique_id=current_user.boutique_id).all()

def rech_facture():
    return Facture.query.filter(Facture.cash==True, Facture.montant >=1, Facture.annule==False, Facture.boutique_id==current_user.boutique_id).all()

def rech_facture_dette():
    return Facture.query.filter(Facture.dette==True, Facture.montant >=1, Facture.annule==False, Facture.boutique_id==current_user.boutique_id).all()

def rech_facture_acompte():
    return Facture.query.filter(Facture.vente_acompte==True, Facture.montant >=1, Facture.annule==False, Facture.boutique_id==current_user.boutique_id).all()



class FactureForm(FlaskForm):
    codefacture=StringField('Code facture', validators=[DataRequired("Completer le code facture"),  Length(min=4, max=200, message="Respecter la procedure")])
    client_input=StringField('Client')
    client_input_cherch=QuerySelectField(query_factory=rech_client, get_label='nom_client', allow_blank=False)
    date_op= StringField('Date', validators=[DataRequired("Completer la date"),  Length(min=10, max=200, message="Format 02-02-2020")])
    submit = SubmitField('Ajouter facture')
    # Vérification des champs entrées
    def validate_date_op(self, date_op):
        date=date_op.data
        result = re.findall(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", date)
        if result:
            pass
        else:
            raise ValidationError("La date doit respectée cette format jj-mm-aaaa")
  
    #Verification des données
    def validate_client_input_cherch(self, client_input_cherch):
        client=client_input_cherch.data
        if client is None:
            client_input_cherch.data=None

class VenteFactureForm(FlaskForm):
    quantite=IntegerField('La quantité', validators=[DataRequired("La quantité svp")])
    prix_vente_detaille = DecimalField('Prix achat')
    produit_vente=QuerySelectField(query_factory=rech_produit_boutique, get_label='nom_produit', allow_blank=False)
    submit = SubmitField('Ajouter sur la facture')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_quantite(self, quantite):
        quantite_o=quantite.data
        if quantite_o <= 0:
            raise ValidationError("Quantité doit être superieure à Zero")


class DiminutionFactureForm(FlaskForm):
    d_quantite=IntegerField('La quantité', validators=[DataRequired("La quantité svp")])
    submit = SubmitField('Ajouter sur la facture')
    #Foction de la verification d'unique existenace dans la base des données
    def validate_d_quantite(self, d_quantite):
        quantite_o=d_quantite.data
        if quantite_o <= 0:
            raise ValidationError("Quantité doit être superieure à Zero")


class VenteFactureGForm(FlaskForm):
    quantite=IntegerField('La quantité', validators=[DataRequired("La quantité svp")])
    prix_vente_gros = DecimalField('Prix achat')
    nomination= SelectField('nomination',choices=[('Quart', 'Quart'), ('Demi', 'Demi'), ('Entier', 'Entier')])
    produit_vente=QuerySelectField(query_factory=rech_produit_boutique, get_label='nom_produit', allow_blank=False)
    submit = SubmitField('Ajouter sur la facture')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_quantite(self, quantite):
        quantite_o=quantite.data
        if quantite_o <= 0:
            raise ValidationError("Quantité doit être superieure à Zero")


class DiminutionGFactureForm(FlaskForm):
    d_quantite=IntegerField('La quantité', validators=[DataRequired("La quantité svp")])
    nomination_d= SelectField('nomination',choices=[('Quart', 'Quart'), ('Demi', 'Demi'), ('Entier', 'Entier')])
    submit = SubmitField('Ajouter sur la facture')
    #Foction de la verification d'unique existenace dans la base des données
    def validate_d_quantite(self, d_quantite):
        quantite_o=d_quantite.data
        if quantite_o <= 0:
            raise ValidationError("Quantité doit être superieure à Zero")


class RechercheFactureForm(FlaskForm):
    facture_client=QuerySelectField(query_factory=rech_facture, get_label='code_facture', allow_blank=True, blank_text="Chercher la facture ")
    submit = SubmitField('Facture')


class RechercheDFactureForm(FlaskForm):
    facture_client=QuerySelectField(query_factory=rech_facture_dette, get_label='code_facture', allow_blank=True, blank_text="Chercher la facture ")
    submit = SubmitField('Facture')

class RechercheAFactureForm(FlaskForm):
    facture_client=QuerySelectField(query_factory=rech_facture_acompte, get_label='code_facture', allow_blank=True, blank_text="Chercher la facture ")
    submit = SubmitField('Facture')


class PayementFactureForm(FlaskForm):
    payement_facture= DecimalField('Prix achat')
    submit = SubmitField('Facture')
    def validate_payement_facture(self, payement_facture):
        payer=payement_facture.data
        if payer <= 0:
            raise ValidationError("Le montant doit être supérieur à 0")


        