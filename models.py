from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Yetkiler (JSON veya ayrı sütunlar olabilir, basitlik için sütun yapıyoruz)
    can_add = db.Column(db.Boolean, default=False)
    can_edit = db.Column(db.Boolean, default=False)
    can_delete = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    musteri_kodu = db.Column(db.String(50), nullable=False)
    magaza_ismi = db.Column(db.String(150), nullable=False)
    magaza_kategorisi = db.Column(db.String(100))
    magaza_sinifi = db.Column(db.String(50))
    cari = db.Column(db.String(100))
    il = db.Column(db.String(50))
    ilce = db.Column(db.String(50))
    bolge = db.Column(db.String(50))
    enlem = db.Column(db.Float)
    boylam = db.Column(db.Float)
    adres = db.Column(db.Text)