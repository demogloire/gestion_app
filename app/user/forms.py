from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
import re
import phonenumbers

from ..models import User, Boutique, Depot

def rech_boutique():
    return Boutique.query.all()

def rech_depot():
    return Depot.query.all()

class AjoutUserForm(FlaskForm):
    nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    #phone= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=125, message="Veuillez respecté les caractères")])
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=125, message="Veuillez respecté les caractères")])
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    password= PasswordField('Mot de passe', validators=[DataRequired("Completer votre mot de passe"),  Length(min=6, max=13, message="Veuillez respecté les caractères")])
    confirm_password= PasswordField('Confirmer mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe'), EqualTo('password')])
    boutique_users= QuerySelectField(query_factory=rech_boutique, get_label='nom_boutique', allow_blank=False)
    avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])
    role= SelectField('Rôle',choices=[('Gérant', 'Gérant'), ('Magasinier', 'Magasinier'), ('Vendeur', 'Vendeur'), ('Associé', 'Associé') ])
    depot_users= QuerySelectField(query_factory=rech_depot, get_label='nom_depot', allow_blank=False)

    submit = SubmitField('Ajouter user')

        #Foction de la verification d'unique existencce dans la base des données
    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Cet utilisateur existe déjà")
    
    # def validate_phone(self, phone):
    #     try:
    #         p = phonenumbers.parse(phone.data)
    #         if not phonenumbers.is_valid_number(p):
    #             raise ValueError()
    #     except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
    #         raise ValidationError('Invalid phone number')

    #Numero de téléphone. validation
    def validate_tel(self, tel):
        tel=tel.data
        ver='^(00|\+[1-9] )[1-9]'
        result = re.match(ver, tel)
        if result:
            pass
        else:
            raise ValidationError("La forme du numéro de téléphone est ex: 002439999999999")

class EditUserForm(FlaskForm):
    nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=13, message="Veuillez respecté les caractères")])
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    boutique_users= QuerySelectField(query_factory=rech_boutique, get_label='nom_boutique', allow_blank=False)
    avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])
    role= SelectField('Rôle',choices=[('Gérant', 'Gérant'), ('Magasinier', 'Magasinier'), ('Vendeur', 'Vendeur'), ('Associé', 'Associé') ])
    depot_users= QuerySelectField(query_factory=rech_depot, get_label='nom_depot', allow_blank=False)

    submit = SubmitField('Ajouter user')

class PassuserForm(FlaskForm):
    password= PasswordField('Mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe')])
    confirm_password= PasswordField('Confirmer mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe'), EqualTo('password',message="Les mots des passes ne pas conforment")])
    submit = SubmitField('Changer mot de passe')



class SuperAjoutUserForm(FlaskForm):
    nom= StringField('Nom', validators=[DataRequired("Completer le nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    post_nom= StringField('Post-Nom', validators=[DataRequired("Completer le post-nom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    prenom= StringField('Prénom', validators=[DataRequired("Completer le prenom"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    adress= StringField('Adresse', validators=[DataRequired("Completer l'adresse"),  Length(min=2, max=200, message="Veuillez respecté les caractères")])
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=233, message="Veuillez respecté les caractères")])
    email= StringField('Email', validators=[DataRequired('Veuillez completer votre email'), Email('Votre email est incorrect')])
    password= PasswordField('Mot de passe', validators=[DataRequired("Completer votre mot de passe"),  Length(min=6, max=13, message="Veuillez respecté les caractères")])
    confirm_password= PasswordField('Confirmer mot de passe', validators=[DataRequired('Veuillez completer votre mot de passe'), EqualTo('password')])
    avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])
    role= SelectField('Rôle',choices=[('Gérant', 'Gérant')])


    submit = SubmitField('Ajouter user')

        #Foction de la verification d'unique existencce dans la base des données
    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Cet utilisateur existe déjà")


class InformationEntrepriseForm(FlaskForm):
    denomination= StringField('Dénomination', validators=[DataRequired("Completer la dénomination de l'entreprise"),  Length(min=2, max=125, message="Veuillez respecté les caractères")])
    personalite = StringField('Personnalité', validators=[DataRequired("Completer les documents de l'entreprise "),  Length(min=2, max=255, message="Veuillez respecté les caractères")])
    adresse = StringField('Adresse', validators=[DataRequired("Adresse de l'entreprise"),  Length(min=2, max=255, message="Veuillez respecté les caractères")])
    siege_social= StringField('Siège social', validators=[DataRequired("Completer le siège de l'entreprise"),  Length(min=2, max=125, message="Veuillez respecté les caractères")])
    telephone= StringField('Téléphone', validators=[DataRequired("Numero téléphone"),  Length(min=8, max=125, message="Veuillez respecté les caractères")])
    email= StringField('Email', validators=[Email('Votre email est incorrect')])
    fax= StringField('Fax')
    avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])

    submit = SubmitField("Les informations de l'entreprise")

    #Numero de téléphone. validation
    def validate_telephone(self, telephone):
        tel=telephone.data
        ver='^(00|\+[1-9] )[1-9]'
        result = re.match(ver, tel)
        if result:
            pass
        else:
            raise ValidationError("La forme du numéro de téléphone est ex: 002439999999999")

