import os
import secrets
from flask import flash, url_for, redirect
from PIL import Image
from .. import create_app
from .. import db

from ..models import Produit 
from . import user

config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/user', picture_fn)
    output_sz = (240,180)
    i= Image.open(form_picture)
    i.thumbnail(output_sz)
    i.save(picture_path)
    return picture_fn

def codeproduit():
    #Verfification de l'identification du produit
    produi_id=Produit.query.order_by(Produit.id.desc()).first()
    id_prod=None
    if produi_id is None:
        id_prod=1
    else:
        id_prod=produi_id.id+1
    codeproduit="#{}".format(id_prod) #Code partielle du produit
    return codeproduit


def verification_de_role(role, droit_b, droit_d):
    ver="Faux"
    ver_b="Ok"
    if role=="Gérant" or role=="Associé":
        if droit_b !="Aucun" or droit_d !="Aucun":
            flash("Le Gérant ou l'Associé, ne peut être associé à un dépôt ou boutique","danger")
            return ver
        else:
            return ver_b
    if role == "Vendeur":
        if droit_b=="Aucun" and droit_d!="Aucun":
            flash("Le vendeur est associé à une boutiqe","danger")
            return ver
        else:
            return ver_b
    if role == "Magasinier":
        if droit_b!="Aucun" and droit_d=="Aucun":
            flash("Magasinier est associé à un dépôt","danger")
            return ver
        else:
            return ver_b
