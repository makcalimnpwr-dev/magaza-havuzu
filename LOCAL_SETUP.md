# Yerel Geliştirme Ortamı Kurulumu

## 1. Python Sanal Ortamı Oluşturma

### Windows (PowerShell):
```powershell
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı aktif et
.\venv\Scripts\Activate.ps1
```

### Windows (CMD):
```cmd
# Sanal ortam oluştur
python -m venv venv

# Sanal ortamı aktif et
venv\Scripts\activate.bat
```

### Mac/Linux:
```bash
# Sanal ortam oluştur
python3 -m venv venv

# Sanal ortamı aktif et
source venv/bin/activate
```

## 2. Bağımlılıkları Yükleme

Sanal ortam aktif olduktan sonra:

```bash
pip install -r requirements.txt
```

## 3. Veritabanını Başlatma

### SQLite Kullanarak (Yerel Geliştirme):

```bash
# Python ile
python init_db.py

# Veya Flask CLI ile
flask create-admin
```

## 4. Uygulamayı Çalıştırma

### Yöntem 1: Python ile (Geliştirme Modu)

```bash
python app.py
```

Uygulama `http://localhost:5000` adresinde çalışacak.

### Yöntem 2: Flask CLI ile

```bash
flask run
```

Veya belirli bir port ile:

```bash
flask run --port 5000
```

### Yöntem 3: Gunicorn ile (Production benzeri)

```bash
gunicorn app:app
```

## 5. İlk Giriş

Tarayıcıda `http://localhost:5000` adresine gidin:

- **Kullanıcı adı:** `admin`
- **Şifre:** `admin123`

## 6. Veritabanı Ayarları

Yerel geliştirme için SQLite kullanılır (varsayılan). 

PostgreSQL kullanmak isterseniz:

1. PostgreSQL kurun ve bir veritabanı oluşturun
2. `app.py` dosyasında `DATABASE_URL` environment variable'ını ayarlayın:

```bash
# Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/dbname"

# Windows CMD
set DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Mac/Linux
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
```

## 7. Sorun Giderme

### Port zaten kullanılıyor hatası:
```bash
# Farklı bir port kullan
flask run --port 5001
```

### Modül bulunamadı hatası:
- Sanal ortamın aktif olduğundan emin olun
- `pip install -r requirements.txt` komutunu tekrar çalıştırın

### Veritabanı hatası:
- `python init_db.py` komutunu çalıştırın
- `instance/database.db` dosyasının oluştuğunu kontrol edin

## 8. Geliştirme İpuçları

- **Debug modu:** `app.py` dosyasında `app.run(debug=True)` zaten aktif
- **Otomatik yenileme:** Kod değişikliklerinde sayfa otomatik yenilenir
- **Loglar:** Terminal'de hata mesajlarını görebilirsiniz

## 9. Durdurma

Uygulamayı durdurmak için terminal'de `Ctrl+C` tuşlarına basın.

