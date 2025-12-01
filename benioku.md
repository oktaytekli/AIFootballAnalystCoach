AI Football Analyst Pro, YouTube üzerindeki futbol maçlarını gerçek zamanlı olarak izleyen, bilgisayarlı görü (Computer Vision) ve üretken yapay zeka (Generative AI) kullanarak taktiksel analizler yapan gelişmiş bir Python aracıdır.

Sistem, oyuncuları ve topu takip eder, topla oynama oranlarını tahmin eder ve Google Gemini desteğiyle "Sanal Teknik Direktör" yorumları yapar.

-- Özellikler --
    Canlı Maç İzleme: YouTube linklerini (HLS akışı) donmadan işler.
    Akıllı Nesne Takibi (Object Tracking): YOLOv8 ve ByteTrack kullanarak oyuncu kimliklerini (ID) hafızada tutar, titremeyi önler.
    Dinamik Takım Kurulumu: Maç başında formaya tıklayarak renkleri otomatik algılar.
    Dashboard Modu: Bilgisayarı yormayan, sadece istatistiklerin aktığı şık bir bilgi paneli sunar.
    Sanal Teknik Direktör: Google Gemini 2.0 Flash modeli, oyunun gidişatını analiz eder ve yorumlar (Mourinho/Guardiola tarzı).
    Maç Sonu Raporu: Maç bittiğinde verileri okuyup pasta ve radar grafikleri çizer.

🛠️ Kurulum
    Projeyi İndirin: 
        git clone
        cd ai-football-analyst

    Gerekli Kütüphaneleri Yükleyin
        requirements.txt
    
    API Anahtarını Ayarlayın:
        Proje klasöründe .env adında bir dosya oluşturun.
        Google AI Studio'dan aldığınız API anahtarını içine yazın

🎮 Kullanım
    Adım 1: Analizi Başlatın
        Terminali açın ve ana motoru çalıştırın (python main.py)
    
    Adım 2: Takım Kurulumu
        Program başladığında video duracak ve bir pencere açılacaktır:
            Takım 1 için oyuncunun formasına tıklayın ve takım ismini terminale yazın.
            Takım 2 için aynısını yapın.
            Pencere kapanacak ve Canlı İstatistik Paneli (Dashboard) açılacaktır.

    Adım 3:
        Siyah panel üzerinden verileri takip edin.
        Program her 60 saniyede bir otomatik analiz yapar.
        Çıkmak için panele tıklayıp q tuşuna basın.

    Adım 4: Görsel Raporu Alın
        Maç bittikten sonra görsel grafikler oluşturmak için (python visualize_report.py)

📂 Dosya Yapısı
    main.py: Projenin beyni. Arayüzü ve akışı yönetir.
    vision_ai.py: Görüntü işleme ve nesne takibi (YOLO) modülü.
    coach_ai.py: Google Gemini ile iletişim kuran yapay zeka modülü.
    video_stream.py: YouTube videolarını işlenebilir formata çeviren modül.
    prompts.py: Yapay zekanın "karakterini" belirleyen talimatlar.
    visualize_report.py: Metin raporunu okuyup grafik çizen araç.
    config.py: Ayarların bulunduğu dosya.

⚠️ Gereksinimler
    Python 3.10 veya üzeri
    GPU (Önerilir, daha hızlı analiz için)
    Google Gemini API Key (Ücretsiz alınabilir)