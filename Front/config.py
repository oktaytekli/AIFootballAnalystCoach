import os
from dotenv import load_dotenv

#DOSYA YOLU GARANTİSİ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, 'api.env')

print(f"Ortam değişkenleri yükleniyor: {ENV_PATH}")
load_dotenv(ENV_PATH)
API_KEY = os.getenv("GEMINI_API_KEY")

#Hata Ayıklama (Debug)
if API_KEY:
    print(f"API Anahtarı başarıyla yüklendi: {API_KEY[:5]}...")
else:
    print(f"HATA: Anahtar bulunamadı!")
    print(f"Aranan Yol: {ENV_PATH}")
    print(f"Klasördeki Dosyalar: {os.listdir(BASE_DIR)}")
    
    raise ValueError("ERROR: API Key not found! 'api.env' dosyasının doğru yerde ve isminin doğru olduğundan emin olun.")

#VİDEO AYARLARI
VIDEO_URL = "urlyeri"
START_TIME_SEC = 80
GEMINI_MODEL = 'gemini-2.0-flash'

#DEFAULT TEAM SETTINGS
TEAMS = {
    "TEAM_1": {
        "NAME": "Team A",
        "LOWER": [20, 100, 100], 
        "UPPER": [35, 255, 255]
    },
    "TEAM_2": {
        "NAME": "Team B",
        "LOWER": [0, 0, 0],
        "UPPER": [180, 255, 50]
    }
}