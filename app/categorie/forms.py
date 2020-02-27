from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Categorie

class CategorieForm(FlaskForm):
    nom=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])

    submit= SubmitField('Enregister')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_nom(self, nom):
        rubrique= Categorie.query.filter_by(nom_categorie=nom.data.capitalize()).first()
        if rubrique:
            raise ValidationError("Cette catégorie existe déjà")

# class CategorieEditerForm(FlaskForm):
#     nom_ed=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
#                     message="Veuillez respecter la longeur de 4 à 60")])
#     submit= SubmitField('Modifier')

#     #Foction de la verification d'unique existenace dans la base des données
#     def validate_nom_ed(self, nom_ed):
#         categorisation= Categorie.query.filter_by(nom=nom_ed.data.capitalize()).first()
#         if categorisation:
#             raise ValidationError("Cette catégorie existe déjà")
