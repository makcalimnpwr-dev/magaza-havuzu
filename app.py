import os
import pandas as pd
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Store
from sqlalchemy import or_

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cok-gizli-bir-anahtar-bunu-degistir')
# Render PostgreSQL için connection string'i düzelt
database_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- YARDIMCI FONKSİYON: FİLTRELEME SORGUSU OLUŞTURUCU ---
def apply_filters(query):
    # Formdan gelen verileri al
    f_kod = request.args.get('musteri_kodu')
    f_isim = request.args.get('magaza_ismi')
    f_cari = request.args.get('cari')
    f_ilce = request.args.get('ilce')
    f_il = request.args.get('il')
    f_bolge = request.args.get('bolge')
    f_kategori = request.args.get('kategori')
    f_sinif = request.args.get('sinif')

    # Filtreleri uygula (ilike: büyük/küçük harf duyarsız içerir araması)
    if f_kod:
        query = query.filter(Store.musteri_kodu.ilike(f"%{f_kod}%"))
    if f_isim:
        query = query.filter(Store.magaza_ismi.ilike(f"%{f_isim}%"))
    if f_cari:
        query = query.filter(Store.cari.ilike(f"%{f_cari}%"))
    if f_ilce:
        query = query.filter(Store.ilce.ilike(f"%{f_ilce}%"))
    if f_il:
        query = query.filter(Store.il == f_il)
    if f_bolge:
        query = query.filter(Store.bolge == f_bolge)
    if f_kategori:
        query = query.filter(Store.magaza_kategorisi == f_kategori)
    if f_sinif:
        query = query.filter(Store.magaza_sinifi == f_sinif)
        
    return query

# --- ROTALAR ---

@app.cli.command("create-admin")
def create_admin():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', is_admin=True, can_add=True, can_edit=True, can_delete=True)
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin kullanıcısı oluşturuldu.")
    else:
        print("Admin zaten var.")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Kullanıcı adı veya şifre hatalı.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    query = Store.query
    query = apply_filters(query) # Filtreleri uygula
    stores = query.all()
    
    # Dropdownlar için benzersiz verileri çek (Alfabetik sırayla)
    cities = db.session.query(Store.il).distinct().order_by(Store.il).all()
    regions = db.session.query(Store.bolge).distinct().order_by(Store.bolge).all()
    categories = db.session.query(Store.magaza_kategorisi).distinct().order_by(Store.magaza_kategorisi).all()
    classes = db.session.query(Store.magaza_sinifi).distinct().order_by(Store.magaza_sinifi).all()

    return render_template('dashboard.html', stores=stores, cities=cities, regions=regions, categories=categories, classes=classes)

@app.route('/upload', methods=['POST'])
@login_required
def upload_excel():
    if not current_user.can_add and not current_user.is_admin:
        flash("Yetkiniz yok.", "error")
        return redirect(url_for('dashboard'))

    file = request.files['file']
    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file)
            for _, row in df.iterrows():
                store = Store(
                    musteri_kodu=str(row.get("Müşteri Kodu", "")),
                    magaza_ismi=str(row.get("Mağaza İsmi", "")),
                    magaza_kategorisi=str(row.get("Mağaza Kategorisi", "")),
                    magaza_sinifi=str(row.get("Mağaza Sınıfı", "")),
                    cari=str(row.get("Cari", "")),
                    il=str(row.get("İl", "")),
                    ilce=str(row.get("İlçe", "")),
                    bolge=str(row.get("Bölge", "")),
                    enlem=row.get("Enlem", 0.0),
                    boylam=row.get("Boylam", 0.0),
                    adres=str(row.get("Adres", ""))
                )
                db.session.add(store)
            db.session.commit()
            flash(f'{len(df)} mağaza başarıyla eklendi.', 'success')
        except Exception as e:
            flash(f'Hata oluştu: {str(e)}', 'error')
    else:
        flash('Lütfen geçerli bir Excel dosyası yükleyin.', 'error')
    return redirect(url_for('dashboard'))

@app.route('/download-template')
@login_required
def download_template():
    columns = ["Müşteri Kodu", "Mağaza İsmi", "Mağaza Kategorisi", "Mağaza Sınıfı", "Cari", "İl", "İlçe", "Bölge", "Enlem", "Boylam", "Adres"]
    df = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="magaza_sablon.xlsx", as_attachment=True)

@app.route('/export')
@login_required
def export_data():
    query = Store.query
    query = apply_filters(query) # Aynı filtreleri dışa aktarmada da kullan
    stores = query.all()
    
    data = []
    for s in stores:
        data.append({
            "Müşteri Kodu": s.musteri_kodu, "Mağaza İsmi": s.magaza_ismi,
            "Mağaza Kategorisi": s.magaza_kategorisi, "Mağaza Sınıfı": s.magaza_sinifi,
            "Cari": s.cari, "İl": s.il, "İlçe": s.ilce, "Bölge": s.bolge,
            "Enlem": s.enlem, "Boylam": s.boylam, "Adres": s.adres
        })
        
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="filtrelenmis_magazalar.xlsx", as_attachment=True)

# Veritabanı tablolarını oluştur (Render'da otomatik çalışır)
# Uygulama başlatıldığında tablolar oluşturulur
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Veritabanı başlatma hatası (normal olabilir): {e}")

if __name__ == '__main__':
    app.run(debug=True)