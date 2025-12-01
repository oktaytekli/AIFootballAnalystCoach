import google.generativeai as genai
import config

# Config dosyasındaki anahtarı al
genai.configure(api_key=config.API_KEY)

print("--- SENİN HESABINDAKİ AKTİF MODELLER ---")
try:
    for m in genai.list_models():
        #sadece metin üretebilen (generateContent) modelleri listele
        if 'generateContent' in m.supported_generation_methods:
            #başındaki 'models/' kısmını atıp temiz ismi yazdıralım
            clean_name = m.name.replace("models/", "")
            print(f"✅ {clean_name}")
except Exception as e:
    print(f"hata oluştu: {e}")