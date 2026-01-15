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
    # Formdan gelen verileri al (çoklu seçim desteği ile)
    f_kod_list = request.args.getlist('musteri_kodu')
    f_isim_list = request.args.getlist('magaza_ismi')
    f_cari_list = request.args.getlist('cari')
    f_ilce_list = request.args.getlist('ilce')
    f_il_list = request.args.getlist('il')
    f_bolge_list = request.args.getlist('bolge')
    f_kategori_list = request.args.getlist('kategori')
    f_sinif_list = request.args.getlist('sinif')

    # Filtreleri uygula (çoklu seçim desteği ile)
    if f_kod_list:
        query = query.filter(or_(*[Store.musteri_kodu.ilike(f"%{k}%") for k in f_kod_list if k]))
    if f_isim_list:
        query = query.filter(or_(*[Store.magaza_ismi.ilike(f"%{i}%") for i in f_isim_list if i]))
    if f_cari_list:
        query = query.filter(or_(*[Store.cari.ilike(f"%{c}%") for c in f_cari_list if c]))
    if f_ilce_list:
        query = query.filter(or_(*[Store.ilce.ilike(f"%{ilce}%") for ilce in f_ilce_list if ilce]))
    if f_il_list:
        query = query.filter(Store.il.in_([il for il in f_il_list if il]))
    if f_bolge_list:
        query = query.filter(Store.bolge.in_([b for b in f_bolge_list if b]))
    if f_kategori_list:
        query = query.filter(Store.magaza_kategorisi.in_([k for k in f_kategori_list if k]))
    if f_sinif_list:
        query = query.filter(Store.magaza_sinifi.in_([s for s in f_sinif_list if s]))
        
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
    
    # Dropdownlar için benzersiz verileri çek (Alfabetik sırayla, None değerleri filtrele)
    cities = [c[0] for c in db.session.query(Store.il).distinct().order_by(Store.il).all() if c[0]]
    regions = [r[0] for r in db.session.query(Store.bolge).distinct().order_by(Store.bolge).all() if r[0]]
    categories = [cat[0] for cat in db.session.query(Store.magaza_kategorisi).distinct().order_by(Store.magaza_kategorisi).all() if cat[0]]
    classes = [cls[0] for cls in db.session.query(Store.magaza_sinifi).distinct().order_by(Store.magaza_sinifi).all() if cls[0]]
    caris = [c[0] for c in db.session.query(Store.cari).distinct().order_by(Store.cari).all() if c[0]]
    ilces = [i[0] for i in db.session.query(Store.ilce).distinct().order_by(Store.ilce).all() if i[0]]
    musteri_kodlari = [m[0] for m in db.session.query(Store.musteri_kodu).distinct().order_by(Store.musteri_kodu).all() if m[0]]
    magaza_isimleri = [m[0] for m in db.session.query(Store.magaza_ismi).distinct().order_by(Store.magaza_ismi).all() if m[0]]

    return render_template('dashboard.html', 
                         stores=stores, 
                         cities=cities, 
                         regions=regions, 
                         categories=categories, 
                         classes=classes,
                         caris=caris,
                         ilces=ilces,
                         musteri_kodlari=musteri_kodlari,
                         magaza_isimleri=magaza_isimleri)

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
    
    # Sütun sıralaması ve görünürlüğü (frontend'den gelecek veya varsayılan)
    column_order = request.args.get('columns', '').split(',') if request.args.get('columns') else []
    
    # Sütun eşleştirmesi
    column_mapping = {
        'musteri_kodu': 'Müşteri Kodu',
        'magaza_ismi': 'Mağaza İsmi',
        'magaza_kategorisi': 'Mağaza Kategorisi',
        'magaza_sinifi': 'Mağaza Sınıfı',
        'bolge': 'Bölge',
        'il': 'İl',
        'ilce': 'İlçe',
        'cari': 'Cari',
        'adres': 'Adres',
        'enlem': 'Enlem',
        'boylam': 'Boylam'
    }
    
    # Varsayılan sıralama (tüm sütunlar)
    if not column_order or column_order == ['']:
        column_order = ['musteri_kodu', 'magaza_ismi', 'magaza_sinifi', 'magaza_kategorisi', 
                       'bolge', 'il', 'ilce', 'cari', 'adres', 'enlem', 'boylam']
    
    # Sadece geçerli sütunları filtrele
    valid_columns = [col for col in column_order if col in column_mapping]
    
    data = []
    for s in stores:
        row = {}
        for col_key in valid_columns:
            col_name = column_mapping[col_key]
            if col_key == 'musteri_kodu':
                row[col_name] = s.musteri_kodu
            elif col_key == 'magaza_ismi':
                row[col_name] = s.magaza_ismi
            elif col_key == 'magaza_kategorisi':
                row[col_name] = s.magaza_kategorisi
            elif col_key == 'magaza_sinifi':
                row[col_name] = s.magaza_sinifi
            elif col_key == 'bolge':
                row[col_name] = s.bolge
            elif col_key == 'il':
                row[col_name] = s.il
            elif col_key == 'ilce':
                row[col_name] = s.ilce
            elif col_key == 'cari':
                row[col_name] = s.cari
            elif col_key == 'adres':
                row[col_name] = s.adres
            elif col_key == 'enlem':
                row[col_name] = s.enlem
            elif col_key == 'boylam':
                row[col_name] = s.boylam
        data.append(row)
        
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return send_file(output, download_name="filtrelenmis_magazalar.xlsx", as_attachment=True)

# Veritabanı tablolarını oluştur ve admin kullanıcısını ekle (Render'da otomatik çalışır)
# Uygulama başlatıldığında tablolar oluşturulur
def init_database():
    """Veritabanını başlat ve admin kullanıcısını oluştur"""
    try:
        print("Veritabanı bağlantısı kontrol ediliyor...")
        db.create_all()
        print("Veritabanı tabloları oluşturuldu.")
        
        # Admin kullanıcısı yoksa oluştur
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                is_admin=True,
                can_add=True,
                can_edit=True,
                can_delete=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin kullanıcısı oluşturuldu: admin / admin123")
        else:
            print("ℹ️ Admin kullanıcısı zaten mevcut.")
    except Exception as e:
        print(f"❌ Veritabanı başlatma hatası: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())

# Uygulama başlatıldığında veritabanını başlat
with app.app_context():
    init_database()

if __name__ == '__main__':
    app.run(debug=True)