v2.0 - Web Platformu Dönüşümü & SaaS Altyapısı
Bu güncelleme ile proje, yerel çalışan bir Python scripti olmaktan çıkıp, Flask tabanlı modern bir web uygulamasına dönüştürülmüştür.

Yeni Özellikler:

Web Arayüzü (Frontend):
    Landing Page: Tailwind CSS ile tasarlanmış, animasyonlu (AOS, Typed.js) ve video arka planlı tanıtım sayfası.
    Dashboard: Kullanıcıların analizleri yönetebileceği, genişletilebilir sidebar'a sahip profesyonel yönetim paneli.
    Login Sistemi: B2B odaklı, sadece yetkili (Admin) girişine izin veren güvenlik katmanı.

Analiz Kurulum Sihirbazı (Wizard):
    Video linki girildikten sonra otomatik kare (snapshot) alma.
    Fotoğraf üzerinden tıklayarak Gerçek Renk (RGB/HEX) seçimi.
    İntroyu geçmek için başlangıç dakikası belirleme.

Token & Bakiye Sistemi:
    Analiz süresine göre maliyet hesaplama (1 dk = 1 Token).
    Yetersiz bakiye durumunda işlemi kısıtlama ve "Bakiyem Kadar Oynat" seçeneği.
    Basit veritabanı (users.json) ile bakiye takibi.

Video Kontrol Merkezi:
    Web üzerinden videoyu Durdurma / Oynatma / İleri-Geri Sarma özellikleri.
    Takım isimlerini analiz sırasında anlık olarak değiştirme imkanı.

Performans & Backend:
    Threading: Video işleme ve Web sunucusu (Flask) ayrıldı. Sekme değiştirilse bile analiz arka planda kesintisiz devam eder.
    Canlı Veri Akışı: AJAX/Fetch API ile sayfa yenilenmeden skor ve yapay zeka yorumları güncellenir.