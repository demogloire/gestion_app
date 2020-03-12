from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField


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
    tel= StringField('Adresse', validators=[DataRequired("Completer le téléphone"),  Length(min=10, max=13, message="Veuillez respecté les caractères")])
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

