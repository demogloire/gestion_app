from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Boutique

class BoutiqueForm(FlaskForm):
    nom_boutique=StringField('Boutique', validators=[DataRequired("Completer nom de la boutique"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
                    
    submit= SubmitField('Enregister')
    #Foction de la verification d'unique existenace dans la base des données
    def validate_nom_boutique(self, nom_boutique):
        boutique=Boutique.query.filter_by(nom_boutique=nom_boutique.data.capitalize()).first()
        if boutique:
            raise ValidationError("Cette boutique existe déjà")



class BoutiqueEditerForm(FlaskForm):
    nom_boutique=StringField('Boutique', validators=[DataRequired("Completer nom de la boutique"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
                    
    submit= SubmitField('Enregister')
    #Foction de la verification d'unique existenace dans la base des données
    def validate_nom_boutique(self, nom_boutique):
        boutique=Boutique.query.filter_by(nom_boutique=nom_boutique.data.capitalize()).first()
        if boutique:
            raise ValidationError("Cette boutique existe déjà")

