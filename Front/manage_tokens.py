import json
import os

DB_FILE = "users.json"

def load_db():
    if not os.path.exists(DB_FILE):
        #Varsayılan admin kullanıcısı
        return {"admin@admin.com": {"password": "1234", "tokens": 20}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def main():
    db = load_db()
    print("\n--- TOKEN YÖNETİM PANELİ ---")
    print("Mevcut Kullanıcılar:")
    for email, data in db.items():
        print(f"- {email}: {data['tokens']} Token")

    email = input("\nİşlem yapılacak email (Varsayılan: admin@admin.com): ") or "admin@admin.com"
    
    if email not in db:
        print("Kullanıcı bulunamadı, yeni oluşturuluyor...")
        db[email] = {"password": "1234", "tokens": 0}

    try:
        amount = int(input("Eklenecek Token Miktarı (Silmek için - eksi girin): "))
        db[email]["tokens"] += amount
        save_db(db)
        print(f"Güncel Bakiye: {db[email]['tokens']} Token")
    except ValueError:
        print("Lütfen sayı girin.")

if __name__ == "__main__":
    main()