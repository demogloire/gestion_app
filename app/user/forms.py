from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField


from ..models import Droit, User

def rech_droit():
    return Droit.query.filter_by(statut=True)


class AjoutUserForm(FlaskForm):
    nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=13, message="Veuillez respecté les caractères")])
    droit_users= QuerySelectField(query_factory=rech_droit, get_label='nom', allow_blank=False)
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    submit = SubmitField('Ajouter user')

class AjoutAdminiForm(FlaskForm):
    nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=13, message="Veuillez respecté les caractères")])
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    submit = SubmitField('Ajouter user')

class EditerUserForm(FlaskForm):
    nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=13, message="Veuillez respecté les caractères")])
    droit_users= QuerySelectField(query_factory=rech_droit, get_label='nom', allow_blank=False)
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    avatar= FileField('Avatar', validators=[FileAllowed(['jpg','png','jpge'],'Seul jpg, png et jpge sont autorisés')])
    
    submit = SubmitField('Ajouter user')

class PassuserForm(FlaskForm):
    password= PasswordField('Mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe')])
    confirm_password= PasswordField('Confirmer mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe'), EqualTo('password',message="Les mots des passes ne pas conforment")])
    submit = SubmitField('Changer mot de passe')

