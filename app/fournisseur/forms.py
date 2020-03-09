from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import re
from ..models import Fournisseur

class FournisseurForm(FlaskForm):
    nom_fourn=StringField('Nom du fournisseur', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    tel_fourn=StringField('N° numero téléphone', validators=[DataRequired("Completer le numéro de téléphone")])
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    adresse= StringField('Adresse', validators=[DataRequired("Veuillez completer l'adresse du founisseur ")])
    
    submit= SubmitField('Enregister')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_nom_fourn(self, nom_fourn):
        fournisseur=Fournisseur.query.filter_by(nom_fourn=nom_fourn.data.upper()).first()
        if fournisseur:
            raise ValidationError("C'est founisseur est dans votre carnet")
    #Foction de la verification du némero de téléphone
    def validate_tel_fourn(self, tel_fourn):
        tel=tel_fourn.data
        ver='^(00|\+[1-9] )[1-9]'
        result = re.match(ver, tel)
        if result:
            pass
        else:
            raise ValidationError("La forme du numéro de téléphone est ex: 002439999999999")

class CategorieEditerForm(FlaskForm):
    nom=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    submit= SubmitField('Modifier')

    #Foction de la verification d'unique existencce dans la base des données
    def validate_nom(self, nom):
        categorisation= Categorie.query.filter_by(nom_categorie=nom.data.capitalize()).first()
        if categorisation:
            raise ValidationError("Cette catégorie existe déjà")

