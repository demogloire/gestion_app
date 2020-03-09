from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField,IntegerField, DecimalField
from wtforms.validators import DataRequired, Length,Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Categorie, Produit


def rech_cate():
    return Categorie.query.all()

class ProduitJForm(FlaskForm):
    nom_produit=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    description=TextAreaField('Contenu', validators=[DataRequired("Description du produit")])
    prix_achat = DecimalField('Prix achat', validators=[DataRequired("Le prix d'achat en decimal")])
    prix_vente = DecimalField('Prix vente', validators=[DataRequired("Le prix de vente en decimal")])
    prix_achat_g = DecimalField('Prix achat', validators=[DataRequired("Le prix d'achat en decimal")])
    prix_vente_g = DecimalField('Prix vente', validators=[DataRequired("Le prix de vente en decimal")])
    emballage= SelectField('Emballage',choices=[('Box', 'Box'), ('Carton', 'Carton'), ('Sac', 'Sac'), ('Vrac', 'Vrac')])
    nombre_contenu=IntegerField('Nombre de contenu')
    avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])
    categorie= QuerySelectField(query_factory=rech_cate, get_label='nom_categorie', allow_blank=False)

    submit= SubmitField('Enregister')

class ProduitAForm(FlaskForm):
    nom_produit=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    description=TextAreaField('Contenu', validators=[DataRequired("Description du produit")])
    prix_achat = DecimalField('Prix achat', validators=[DataRequired("Le prix d'achat en decimal")])
    prix_vente = DecimalField('Prix vente', validators=[DataRequired("Le prix de vente en decimal")])
    prix_achat_g = DecimalField('Prix achat', validators=[DataRequired("Le prix d'achat en decimal")])
    prix_vente_g = DecimalField('Prix vente', validators=[DataRequired("Le prix de vente en decimal")])
    emballage= SelectField('Emballage',choices=[('Box', 'Box'), ('Carton', 'Carton'), ('Sac', 'Sac'), ('Vrac', 'Vrac')])
    nombre_contenu=IntegerField('Nombre de contenu')
    avatar = FileField("Image",validators=[FileAllowed(['jpg','png'],'Seul jpg et png sont autorisés')])
    categorie= QuerySelectField(query_factory=rech_cate, get_label='nom_categorie', allow_blank=False)

    submit= SubmitField('Enregister')

""" 
class CategorieEditerForm(FlaskForm):
    nom=StringField('Nom', validators=[DataRequired("Completer nom"),  Length(min=4, max=60, 
                    message="Veuillez respecter la longeur de 4 à 60")])
    submit= SubmitField('Modifier')

    #Foction de la verification d'unique existencce dans la base des données
    def validate_nom(self, nom):
        categorisation= Categorie.query.filter_by(nom_categorie=nom.data.capitalize()).first()
        if categorisation:
            raise ValidationError("Cette catégorie existe déjà")

 """