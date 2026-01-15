# Render Deployment Rehberi

Bu proje Render platformunda çalışacak şekilde yapılandırılmıştır.

## Özellikler

- ✅ PostgreSQL veritabanı kullanımı (veriler kalıcı)
- ✅ Sadece kod değişikliklerinde deploy
- ✅ Veri değişiklikleri deploy gerektirmez
- ✅ Render üzerinden mağaza verilerini yönetme

## Render'a Deploy Etme

### 1. GitHub'a Push Edin

```bash
git init
git add .
git commit -m "Render deployment için hazırlandı"
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```

### 2. Render Dashboard'da Yapılandırma

#### Seçenek A: render.yaml Kullanarak (Önerilen)

1. Render Dashboard'a giriş yapın
2. "New" > "Blueprint" seçin
3. GitHub repository'nizi bağlayın
4. Render otomatik olarak `render.yaml` dosyasını okuyacak ve servisleri oluşturacak

#### Seçenek B: Manuel Yapılandırma

**PostgreSQL Database:**
1. "New" > "PostgreSQL" seçin
2. Database adı: `magaza-veritabani`
3. Plan seçin (Free plan yeterli başlangıç için)

**Web Service:**
1. "New" > "Web Service" seçin
2. GitHub repository'nizi bağlayın
3. Ayarlar:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment Variables:**
     - `DATABASE_URL`: PostgreSQL database'in connection string'i (Render otomatik sağlar)
     - `SECRET_KEY`: Güvenli bir secret key (Render'ın generate etmesine izin verin)
     - `PYTHON_VERSION`: `3.13.0`

### 3. İlk Deploy Sonrası

İlk deploy'dan sonra admin kullanıcısı oluşturmak için:

1. Render Dashboard'da web service'inize gidin
2. "Shell" sekmesine tıklayın
3. Şu komutu çalıştırın:
   ```bash
   python init_db.py
   ```

Veya Flask CLI kullanarak:
```bash
flask create-admin
```

**Varsayılan Admin Bilgileri:**
- Kullanıcı adı: `admin`
- Şifre: `admin123`

⚠️ **GÜVENLİK:** İlk girişten sonra mutlaka şifreyi değiştirin!

## Veri Yönetimi

### Mağaza Verilerini Ekleme/Güncelleme

1. Render'da deploy edilmiş web uygulamanıza giriş yapın
2. Dashboard'dan Excel dosyası yükleyerek mağaza ekleyin
3. Veriler PostgreSQL veritabanında kalıcı olarak saklanır
4. Kod değişikliği olmadığı sürece deploy gerekmez

### Veritabanı Yedekleme

Render Dashboard'dan PostgreSQL database'inize gidip "Backups" sekmesinden yedek alabilirsiniz.

## Önemli Notlar

- ✅ Veriler PostgreSQL'de saklanır, deploy'larda kaybolmaz
- ✅ Sadece kod değişikliği olduğunda deploy yapılır
- ✅ Veri ekleme/güncelleme için deploy gerekmez
- ✅ `instance/` klasörü `.gitignore`'da, SQLite dosyaları commit edilmez

## Sorun Giderme

### Veritabanı Bağlantı Hatası

- `DATABASE_URL` environment variable'ının doğru ayarlandığından emin olun
- PostgreSQL servisinin çalıştığından emin olun

### Tablolar Oluşmadı

- Render Shell'den `python init_db.py` komutunu çalıştırın
- Veya `flask create-admin` komutunu kullanın

### Gunicorn Hatası

- `requirements.txt`'de `gunicorn` olduğundan emin olun
- Start command'in `gunicorn app:app` olduğunu kontrol edin


