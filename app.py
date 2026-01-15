import os
import pandas as pd
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Store, CustomColumn, AllowedValue
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
        kod_filtered = [k for k in f_kod_list if k]
        if kod_filtered:
            query = query.filter(or_(*[Store.musteri_kodu.ilike(f"%{k}%") for k in kod_filtered]))
    if f_isim_list:
        isim_filtered = [i for i in f_isim_list if i]
        if isim_filtered:
            query = query.filter(or_(*[Store.magaza_ismi.ilike(f"%{i}%") for i in isim_filtered]))
    if f_cari_list:
        cari_filtered = [c for c in f_cari_list if c]
        if cari_filtered:
            query = query.filter(or_(*[Store.cari.ilike(f"%{c}%") for c in cari_filtered]))
    if f_ilce_list:
        ilce_filtered = [ilce for ilce in f_ilce_list if ilce]
        if ilce_filtered:
            query = query.filter(or_(*[Store.ilce.ilike(f"%{ilce}%") for ilce in ilce_filtered]))
    if f_il_list:
        il_filtered = [il for il in f_il_list if il]
        if il_filtered:
            query = query.filter(Store.il.in_(il_filtered))
    if f_bolge_list:
        bolge_filtered = [b for b in f_bolge_list if b]
        if bolge_filtered:
            query = query.filter(Store.bolge.in_(bolge_filtered))
    if f_kategori_list:
        kategori_filtered = [k for k in f_kategori_list if k]
        if kategori_filtered:
            query = query.filter(Store.magaza_kategorisi.in_(kategori_filtered))
    if f_sinif_list:
        sinif_filtered = [s for s in f_sinif_list if s]
        if sinif_filtered:
            query = query.filter(Store.magaza_sinifi.in_(sinif_filtered))
        
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
            print("[OK] Admin kullanıcısı oluşturuldu: admin / admin123")
        else:
            print("[INFO] Admin kullanıcısı zaten mevcut.")
    except Exception as e:
        print(f"[ERROR] Veritabani baslatma hatasi: {type(e).__name__}: {str(e)}")
        import traceback
        print(traceback.format_exc())

# Uygulama başlatıldığında veritabanını başlat
with app.app_context():
    init_database()

# --- MAĞAZA DÜZENLEME ROUTE'LARI ---

@app.route('/store/<int:store_id>')
@login_required
def get_store(store_id):
    """Mağaza bilgilerini getir (AJAX için)"""
    store = Store.query.get_or_404(store_id)
    return jsonify({
        'id': store.id,
        'musteri_kodu': store.musteri_kodu,
        'magaza_ismi': store.magaza_ismi,
        'magaza_kategorisi': store.magaza_kategorisi,
        'magaza_sinifi': store.magaza_sinifi,
        'cari': store.cari,
        'il': store.il,
        'ilce': store.ilce,
        'bolge': store.bolge,
        'enlem': store.enlem,
        'boylam': store.boylam,
        'adres': store.adres,
        'custom_fields': store.custom_fields or {}
    })

@app.route('/store/update', methods=['POST'])
@login_required
def update_store():
    """ID bazlı mağaza güncelleme (sadece belirtilen sütunlar)"""
    if not current_user.can_edit and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    store_id = data.get('id')
    
    if not store_id:
        return jsonify({'success': False, 'message': 'ID gerekli.'}), 400
    
    store = Store.query.get(store_id)
    if not store:
        return jsonify({'success': False, 'message': 'Mağaza bulunamadı.'}), 404
    
    # Sadece gönderilen alanları güncelle
    update_fields = {
        'musteri_kodu': 'musteri_kodu',
        'magaza_ismi': 'magaza_ismi',
        'magaza_kategorisi': 'magaza_kategorisi',
        'magaza_sinifi': 'magaza_sinifi',
        'cari': 'cari',
        'il': 'il',
        'ilce': 'ilce',
        'bolge': 'bolge',
        'enlem': 'enlem',
        'boylam': 'boylam',
        'adres': 'adres'
    }
    
    for key, field in update_fields.items():
        if key in data:
            setattr(store, field, data[key])
    
    # Dinamik sütunlar
    if 'custom_fields' in data:
        store.custom_fields = data['custom_fields']
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Mağaza başarıyla güncellendi.'})

# --- KULLANICI YÖNETİMİ ROUTE'LARI ---

@app.route('/users')
@login_required
def users():
    """Kullanıcı yönetimi sayfası"""
    if not current_user.is_admin:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))
    
    # Sadece admin tüm kullanıcıları görebilir
    users_list = User.query.all()
    
    return render_template('users.html', users=users_list)

@app.route('/users/create', methods=['POST'])
@login_required
def create_user():
    """Yeni kullanıcı oluştur"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten kullanılıyor.'}), 400
    
    user = User(
        username=username,
        is_admin=data.get('is_admin', False),
        can_add=data.get('can_add', False),
        can_edit=data.get('can_edit', False),
        can_delete=data.get('can_delete', False)
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Kullanıcı oluşturuldu.'})

@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user(user_id):
    """Kullanıcı güncelle"""
    if not current_user.is_admin:
        # Admin değilse sadece kendi bilgilerini güncelleyebilir
        if user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'username' in data:
        if User.query.filter(User.username == data['username'], User.id != user_id).first():
            return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten kullanılıyor.'}), 400
        user.username = data['username']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    if current_user.is_admin:
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'can_add' in data:
            user.can_add = data['can_add']
        if 'can_edit' in data:
            user.can_edit = data['can_edit']
        if 'can_delete' in data:
            user.can_delete = data['can_delete']
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Kullanıcı güncellendi.'})

# --- AYARLAR ROUTE'LARI ---

@app.route('/settings')
@login_required
def settings():
    """Ayarlar sayfası"""
    if not current_user.is_admin:
        flash('Bu sayfaya erişim yetkiniz yok.', 'error')
        return redirect(url_for('dashboard'))
    
    custom_columns = CustomColumn.query.filter_by(is_active=True).all()
    allowed_values = {}
    for field in ['il', 'ilce', 'cari', 'bolge', 'magaza_sinifi', 'magaza_kategorisi']:
        allowed_values[field] = [av.value for av in AllowedValue.query.filter_by(field_name=field).all()]
    
    return render_template('settings.html', custom_columns=custom_columns, allowed_values=allowed_values)

@app.route('/settings/column/add', methods=['POST'])
@login_required
def add_custom_column():
    """Dinamik sütun ekle"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    column = CustomColumn(
        column_name=data['column_name'],
        column_label=data['column_label'],
        column_type=data.get('column_type', 'text')
    )
    db.session.add(column)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Sütun eklendi.', 'column': {'id': column.id, 'column_name': column.column_name, 'column_label': column.column_label}})

@app.route('/settings/allowed-value/add', methods=['POST'])
@login_required
def add_allowed_value():
    """İzin verilen değer ekle"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Yetkiniz yok.'}), 403
    
    data = request.get_json()
    field_name = data['field_name']
    values = data.get('values', [])
    
    if isinstance(values, str):
        values = [v.strip() for v in values.split('\n') if v.strip()]
    
    added = []
    for value in values:
        if not AllowedValue.query.filter_by(field_name=field_name, value=value).first():
            av = AllowedValue(field_name=field_name, value=value)
            db.session.add(av)
            added.append(value)
    
    db.session.commit()
    return jsonify({'success': True, 'message': f'{len(added)} değer eklendi.', 'added': added})

if __name__ == '__main__':
    app.run(debug=True)