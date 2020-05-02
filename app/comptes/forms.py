from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import login_user, current_user, logout_user, login_required
import re


from ..models import Boutique, Client, Comptes


def rech_compte():
    return Client.query.filter(Client.boutique_id==current_user.boutique_id, Client.nom_client !='Tous').all()

def rech_compte_filter():
    return Comptes.query.filter_by(boutique_id=current_user.boutique_id).all()


class CompteClientForm(FlaskForm):
    nom_compte=StringField('Intitulé compte', validators=[DataRequired("Completer l'intitulé du compte"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    branche_compte=SelectField('Branche du compte',choices=[('Client', 'Client')])
    clients=QuerySelectField(query_factory=rech_compte, get_label='nom_client', allow_blank=False)             
    submit= SubmitField('Enregister')



class CompteEditerForm(FlaskForm):
    nom_compte=StringField('Intitulé compte', validators=[DataRequired("Completer l'intitulé du compte"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    
    submit= SubmitField('Enregister')

class RechercheForm(FlaskForm):
    clients_client=QuerySelectField(query_factory=rech_compte_filter, get_label='num_compte', allow_blank=False) 
    submit= SubmitField('Enregister')


class OperationForm(FlaskForm):
    date_op= StringField('Date', validators=[DataRequired("Completer la date"),  Length(min=10, max=200, message="Format 02-02-2020")])
    description=TextAreaField('Motif de la transanction', validators=[DataRequired("Motif de la transanction")])
    montant = DecimalField('Montant de la transancion', validators=[DataRequired("Le montant est decimal")])
    type_transaction=SelectField('Branche du compte',choices=[('Dépôt', 'Dépôt'),('Retrait ', 'Retrait ')])

    submit= SubmitField('Enregister')
    # Vérification
    def validate_date_op(self, date_op):
        date=date_op.data
        result = re.findall(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", date)
        if result:
            pass
        else:
            raise ValidationError("La date doit respectée cette format jj-mm-aaaa")
    
    def validate_montant(self, montant):
        quantite_o=montant.data
        if quantite_o <= 0:
            raise ValidationError("Le montant doit être supérieur de Zero.")
