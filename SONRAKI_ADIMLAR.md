# Render Deploy Sonrası Adımlar

## ✅ Tamamlananlar
- ✅ PostgreSQL veritabanı oluşturuldu (`magaza-veritabani`)
- ✅ Web Service deploy edildi (`magaza-yonetim-sistemi`)

## 🔧 Yapılması Gerekenler

### 1. DATABASE_URL'yi Web Service'e Ekleyin

1. Render Dashboard'da **`magaza-veritabani`** (PostgreSQL) sayfasına gidin
2. **"Connections"** sekmesine tıklayın
3. **"Internal Database URL"** değerini kopyalayın (şuna benzer: `postgresql://user:pass@host:5432/dbname`)
4. **`magaza-yonetim-sistemi`** (Web Service) sayfasına gidin
5. **"Environment"** sekmesine tıklayın
6. **"Add Environment Variable"** butonuna tıklayın:
   - **Key:** `DATABASE_URL`
   - **Value:** Kopyaladığınız Internal Database URL'yi yapıştırın
7. **"Save Changes"** butonuna tıklayın
8. Web Service otomatik olarak yeniden deploy olacak (1-2 dakika)

### 2. Veritabanı Tablolarını Oluşturun

1. **`magaza-yonetim-sistemi`** (Web Service) sayfasına gidin
2. **"Shell"** sekmesine tıklayın
3. Açılan terminalde şu komutu çalıştırın:
   ```bash
   python init_db.py
   ```
4. Şu mesajları görmelisiniz:
   - "Veritabanı tabloları oluşturuldu."
   - "Admin kullanıcısı oluşturuldu: admin / admin123"

### 3. İlk Giriş

1. Web Service sayfasında sağ üstteki **URL'ye** tıklayın (veya kopyalayın)
2. Giriş sayfasında:
   - **Kullanıcı adı:** `admin`
   - **Şifre:** `admin123`
3. ⚠️ **GÜVENLİK:** İlk girişten sonra mutlaka şifreyi değiştirin!

### 4. Mağaza Verilerini Yükleme

1. Dashboard'a giriş yaptıktan sonra
2. Excel dosyası yükleyerek mağaza verilerini ekleyebilirsiniz
3. Veriler PostgreSQL'de kalıcı olarak saklanır
4. Kod değişikliği olmadığı sürece deploy gerekmez

## 📝 Notlar

- ✅ Veriler PostgreSQL'de saklanır, deploy'larda kaybolmaz
- ✅ Sadece kod değişikliği olduğunda deploy yapılır
- ✅ Veri ekleme/güncelleme için deploy gerekmez
- ⚠️ Bölgeler farklı (Frankfurt vs Oregon) - performans için aynı bölgede olmaları önerilir ama şu an çalışır durumda

## 🔍 Sorun Giderme

### DATABASE_URL Hatası
- Environment variable'ın doğru eklendiğinden emin olun
- Internal Database URL kullandığınızdan emin (External değil)

### Tablolar Oluşmadı
- Shell'den `python init_db.py` komutunu çalıştırın
- Hata mesajı varsa paylaşın

### Web Service Çalışmıyor
- Environment sekmesinde `DATABASE_URL` olduğundan emin olun
- Logs sekmesinden hata mesajlarını kontrol edin


