# Render'a Deploy Etme - Adım Adım Rehber

## 1. Render Hesabı Oluşturma

1. **https://render.com** adresine gidin
2. Sağ üst köşedeki **"Get Started for Free"** veya **"Sign Up"** butonuna tıklayın
3. GitHub hesabınızla giriş yapın (önerilen) veya email ile kayıt olun
4. Email doğrulaması yapın (gerekirse)

## 2. GitHub'a Projeyi Yükleme

Render, GitHub repository'nizden deploy eder. Önce projenizi GitHub'a yükleyin:

### A) GitHub'da Yeni Repository Oluşturma

1. **https://github.com** adresine gidin ve giriş yapın
2. Sağ üst köşede **"+"** > **"New repository"** seçin
3. Repository adı verin (örn: `magaza-yonetim-sistemi`)
4. **Public** veya **Private** seçin (Render her ikisini de destekler)
5. **"Create repository"** butonuna tıklayın
6. GitHub size komutları gösterecek, şimdilik kapatın

### B) Projeyi GitHub'a Push Etme

Proje klasörünüzde (PowerShell veya Terminal'de) şu komutları çalıştırın:

```bash
# Git repository'si başlat (eğer yoksa)
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Render deployment için hazırlandı"

# GitHub repository'nizi ekleyin (YOUR_USERNAME ve REPO_NAME'i değiştirin)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Main branch'e push edin
git branch -M main
git push -u origin main
```

**Örnek:**
```bash
git remote add origin https://github.com/mustafa/magaza-yonetim-sistemi.git
```

## 3. Render'da Blueprint Oluşturma (Önerilen Yöntem)

`render.yaml` dosyası hazır olduğu için en kolay yöntem Blueprint kullanmak:

1. Render Dashboard'a giriş yapın: **https://dashboard.render.com**
2. Sol menüden **"New +"** butonuna tıklayın
3. **"Blueprint"** seçeneğini seçin
4. **"Connect account"** ile GitHub hesabınızı bağlayın (ilk kez ise)
5. Repository'nizi seçin
6. **"Apply"** butonuna tıklayın
7. Render otomatik olarak:
   - PostgreSQL veritabanını oluşturacak
   - Web servisini oluşturacak
   - Bağlantıları yapılandıracak

## 4. Alternatif: Manuel Oluşturma

Eğer Blueprint kullanmak istemezseniz:

### A) PostgreSQL Veritabanı Oluşturma

1. Render Dashboard'da **"New +"** > **"PostgreSQL"** seçin
2. Ayarlar:
   - **Name:** `magaza-veritabani`
   - **Database:** `magazalar`
   - **User:** `magaza_user`
   - **Region:** Size en yakın bölgeyi seçin (örn: Frankfurt)
   - **Plan:** Free (başlangıç için yeterli)
3. **"Create Database"** butonuna tıklayın
4. Veritabanı oluşturulurken bekleyin (1-2 dakika)

### B) Web Service Oluşturma

1. Render Dashboard'da **"New +"** > **"Web Service"** seçin
2. GitHub repository'nizi seçin (veya bağlayın)
3. Ayarlar:
   - **Name:** `magaza-yonetim-sistemi`
   - **Region:** Veritabanıyla aynı bölgeyi seçin
   - **Branch:** `main`
   - **Root Directory:** (boş bırakın)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free (başlangıç için yeterli)
4. **Environment Variables** bölümüne gidin:
   - **Key:** `DATABASE_URL`
     - **Value:** PostgreSQL veritabanınızın **"Internal Database URL"** değerini kopyalayın
     - (Veritabanı sayfasında "Connections" sekmesinde bulabilirsiniz)
   - **Key:** `SECRET_KEY`
     - **Value:** Rastgele bir değer girin (örn: `super-gizli-anahtar-12345`)
     - Veya Render'ın "Generate" butonunu kullanın
5. **"Create Web Service"** butonuna tıklayın

## 5. İlk Deploy ve Veritabanı Kurulumu

### Deploy İşlemi

1. Web service oluşturulduktan sonra otomatik olarak deploy başlar
2. "Events" sekmesinden deploy ilerlemesini takip edebilirsiniz
3. İlk deploy 3-5 dakika sürebilir
4. Deploy tamamlandığında yeşil "Live" yazısını göreceksiniz
5. Sağ üstteki URL'ye tıklayarak sitenize erişebilirsiniz

### Veritabanı Tablolarını Oluşturma

Deploy tamamlandıktan sonra:

1. Web service sayfanızda **"Shell"** sekmesine tıklayın
2. Açılan terminalde şu komutu çalıştırın:
   ```bash
   python init_db.py
   ```
3. Veya alternatif olarak:
   ```bash
   flask create-admin
   ```
4. "Admin kullanıcısı oluşturuldu" mesajını görmelisiniz

## 6. İlk Giriş

1. Web sitenizin URL'sine gidin (Render dashboard'dan kopyalayın)
2. Giriş sayfasında:
   - **Kullanıcı adı:** `admin`
   - **Şifre:** `admin123`
3. Giriş yaptıktan sonra **mutlaka şifreyi değiştirin!**

## 7. Mağaza Verilerini Yükleme

1. Dashboard'a giriş yaptıktan sonra
2. Excel dosyası yükleyerek mağaza verilerini ekleyebilirsiniz
3. Veriler PostgreSQL'de kalıcı olarak saklanır
4. Kod değişikliği olmadığı sürece deploy gerekmez

## Önemli Notlar

- ✅ **Free Plan:** Ücretsiz plan kullanıyorsanız, 15 dakika kullanılmazsa uygulama "sleep" moduna geçer. İlk istekte 30-60 saniye içinde uyanır.
- ✅ **Veritabanı:** PostgreSQL veritabanı her zaman çalışır, veriler kaybolmaz
- ✅ **Deploy:** Sadece kod değişikliği olduğunda deploy yapılır
- ✅ **Güncellemeler:** Mağaza verilerini web arayüzünden güncelleyebilirsiniz, deploy gerekmez

## Sorun Giderme

### Deploy Başarısız Olursa

1. "Events" sekmesinde hata mesajını kontrol edin
2. Genellikle `requirements.txt` veya `DATABASE_URL` sorunları olur
3. `DATABASE_URL`'in doğru olduğundan emin olun

### Veritabanı Bağlantı Hatası

1. PostgreSQL servisinin çalıştığından emin olun
2. `DATABASE_URL` environment variable'ının doğru olduğunu kontrol edin
3. Internal Database URL kullandığınızdan emin olun (External değil)

### Tablolar Oluşmadı

1. Shell'den `python init_db.py` komutunu çalıştırın
2. Hata mesajı varsa paylaşın, birlikte çözelim

## Sonraki Adımlar

- ✅ İlk deploy tamamlandı
- ✅ Admin kullanıcısı oluşturuldu
- ✅ Mağaza verilerini yükleyebilirsiniz
- ✅ Kod değişikliği yaptığınızda otomatik deploy olur (GitHub'a push ettiğinizde)

Başarılar! 🚀


