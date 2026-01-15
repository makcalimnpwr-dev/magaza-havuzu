# Bölge Sorunu Çözümü

## Sorun
PostgreSQL ve Web Service farklı bölgelerde olduğu için Internal Database URL çalışmıyor.

## Çözüm 1: Her İki Servisi Aynı Bölgeye Taşıma (Önerilen)

### PostgreSQL'i Taşıma:
1. PostgreSQL servisi (`magaza-veritabani`) sayfasına gidin
2. "Settings" sekmesine tıklayın
3. "Region" bölümünü bulun
4. Web Service ile aynı bölgeyi seçin (Oregon)
5. "Save Changes" butonuna tıklayın
6. PostgreSQL yeniden oluşturulacak (veriler kaybolabilir - yedek alın!)

### Veya Web Service'i Taşıma:
1. Web Service (`magaza-yonetim-sistemi`) sayfasına gidin
2. "Settings" sekmesine tıklayın
3. "Region" bölümünü bulun
4. PostgreSQL ile aynı bölgeyi seçin (Frankfurt)
5. "Save Changes" butonuna tıklayın

## Çözüm 2: External Database URL Kullanma (Geçici)

Eğer bölge değiştirmek istemiyorsanız:

1. PostgreSQL sayfasında "Connections" sekmesine gidin
2. **"External Database URL"** değerini kopyalayın
3. Web Service'te `DATABASE_URL` environment variable'ını güncelleyin
4. External URL kullanın

⚠️ **Not:** External URL daha yavaş olabilir ve güvenlik açısından ideal değildir.

## Önerilen: Çözüm 1
Her iki servisi aynı bölgeye taşımak en iyi çözümdür.

