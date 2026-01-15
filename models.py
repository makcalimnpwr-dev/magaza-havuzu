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
    # Dinamik sütunlar için JSON alanı
    custom_fields = db.Column(db.JSON, default=dict)

class CustomColumn(db.Model):
    """Dinamik olarak eklenen sütunlar"""
    id = db.Column(db.Integer, primary_key=True)
    column_name = db.Column(db.String(100), nullable=False, unique=True)
    column_label = db.Column(db.String(150), nullable=False)
    column_type = db.Column(db.String(50), default='text')  # text, number, date
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

class AllowedValue(db.Model):
    """İzin verilen değerler (İl, İlçe, Cari, Bölge, Mağaza Sınıfı, Kategori)"""
    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(50), nullable=False)  # il, ilce, cari, bolge, magaza_sinifi, magaza_kategorisi
    value = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    __table_args__ = (db.UniqueConstraint('field_name', 'value', name='unique_field_value'),)