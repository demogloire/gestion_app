from flask_wtf import FlaskForm
import re
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import login_user, current_user, login_required

from ..models import Comptedepense

def rech_rubrique():
    return Comptedepense.query.filter_by(branche_depense='Boutique').all()

class CompteForm(FlaskForm):
    rubrique=StringField('rubrique', validators=[DataRequired("Completer nom de la rubrique"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    branche_depense=SelectField('Branche',choices=[('Dépôt', 'Dépôt'), ('Boutique', 'Boutique')])
                    
    submit= SubmitField('Enregister')


class DepenseForm(FlaskForm):
    branche_depense=QuerySelectField(query_factory=rech_rubrique, get_label='rubrique', allow_blank=False)
    date_op= StringField('Date', validators=[DataRequired("Completer la date"),  Length(min=10, max=200, message="Format 02-02-2020")])
    description=TextAreaField('Contenu', validators=[DataRequired("Description du depense")])
    montant = DecimalField('Montant', validators=[DataRequired("Le montant du dépense")])
    submit= SubmitField('Enregister')

    # Vérification des champs entrées
    def validate_date_op(self, date_op):
        date=date_op.data
        result = re.findall(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", date)
        if result:
            pass
        else:
            raise ValidationError("La date doit respectée cette format jj-mm-aaaa")


