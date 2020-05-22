from flask_wtf import FlaskForm
import re
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import login_user, current_user, login_required

from ..models import Categorie, Typeclient, Produitboutique


def rech_type_client():
    return Typeclient.query.all()

def rech_produit_boutique():
    return Produitboutique.query.filter_by(boutique_id=current_user.boutique_id).all()

class CorrectionForm(FlaskForm):
    quantite=IntegerField('La quantité', validators=[DataRequired("La quantité svp")])
    produit_correct=QuerySelectField(query_factory=rech_produit_boutique, get_label='nom_produit', allow_blank=False)
    submit = SubmitField('Ajouter sur la facture')

    #Foction de la verification d'unique existenace dans la base des données
    def validate_quantite(self, quantite):
        quantite_o=quantite.data
        if quantite_o <= 0:
            raise ValidationError("Quantité doit être superieure à Zero")
