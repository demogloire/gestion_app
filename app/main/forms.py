from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Depot

class DepotForm(FlaskForm):
    nom_depot=StringField('Nom', validators=[DataRequired("Completer nom du dépôt"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])

    submit= SubmitField('Enregister')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_nom_depot(self, nom_depot):
        depot= Depot.query.filter_by(nom_depot=nom_depot.data.capitalize()).first()
        if depot:
            raise ValidationError("C'est dépôt existe déjà")

class DepotEditForm(FlaskForm):
    nom_depot=StringField('Nom', validators=[DataRequired("Completer nom du dépôt"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    submit= SubmitField('Modifier')

    

