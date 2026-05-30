# Swiss Ephemeris Veri Dosyaları

Swiss Ephemeris kütüphanesi hesaplama yapmak için ephemeris veri dosyalarına ihtiyaç duyar. Bu dosyaları indirmek için aşağıdaki komutları çalıştırın:

```bash
# Veri dosyalarını indir (1800-2400 yılı arası için yeterli)
curl -O https://www.astro.com/ftp/swisseph/ephe/seas_18.se1
curl -O https://www.astro.com/ftp/swisseph/ephe/semo_18.se1
curl -O https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1

# ephe klasörüne taşı
mv *.se1 ephe/
```

Bu dosyaları indirdikten sonra, Docker build işlemi sırasında otomatik olarak container'a dahil edilecektir.

## Local Test

```bash
pip install -r requirements.txt
python main.py
```

## Deploy (Render.com)

1. GitHub'a yeni repo oluştur, `ephemeris-service/` klasörünü push et
2. Render.com → New Web Service → GitHub repo seç
3. Environment: Docker
4. Free instance type yeterli (cold start ~30 saniye)
5. Deploy sonrası URL'yi al: `https://ephemeris-service.onrender.com`
