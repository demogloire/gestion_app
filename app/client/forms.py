from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Categorie, Typeclient


def rech_type_client():
    return Typeclient.query.all()

class AjouterClientForm(FlaskForm):
    nom_client=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, message="Veuillez respecter la longeur de 4 à 60")])
    tel_client=StringField('Téléphone', validators=[DataRequired("Completer le numéro de telephone")])
    email= StringField('Email', validators=[DataRequired('Veuillez completer  email'), Email('Votre email est incorrect')])
    adresse=StringField('Adresse', validators=[DataRequired("Completer l'adresse")])
    typeclient_id=QuerySelectField(query_factory=rech_type_client, get_label='nom_type', allow_blank=False)
    submit= SubmitField('Enregister')



class CategorieEditerForm(FlaskForm):
    nom=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    submit= SubmitField('Modifier')

    #Foction de la verification d'unique existencce dans la base des données
    def validate_nom(self, nom):
        categorisation= Categorie.query.filter_by(nom_categorie=nom.data.capitalize()).first()
        if categorisation:
            raise ValidationError("Cette catégorie existe déjà")

