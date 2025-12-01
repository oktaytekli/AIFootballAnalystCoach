from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import cv2
import config
from video_stream import get_direct_url
from vision_ai import VisionEngine
from coach_ai import VirtualCoach
import time
import json
import os
import numpy as np
import threading

app = Flask(__name__)

# 1. VERİTABANI VE TOKEN YÖNETİMİ
DB_FILE = "users.json"

def get_user_tokens(email="admin@admin.com"):
    """Kullanıcının token bakiyesini getirir."""
    if not os.path.exists(DB_FILE): return 0
    with open(DB_FILE, "r") as f:
        data = json.load(f)
        return data.get(email, {}).get("tokens", 0)

def update_user_tokens(email, amount):
    """Token ekler veya çıkarır."""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({email: {"password": "1234", "tokens": 0}}, f)
    
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    
    if email not in data:
        data[email] = {"password": "1234", "tokens": 0}

    current = data[email]["tokens"]
    new_balance = max(0, current + amount)
    data[email]["tokens"] = new_balance
    
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return new_balance

# 2. GLOBAL DURUM VE DEĞİŞKENLER
control_state = {
    "running": False,
    "paused": False,
    "seek_command": 0,
    "end_time_sec": 0,
    "stop_requested": False,
    "team1_name": "Takım A", "team1_hsv": None,
    "team2_name": "Takım B", "team2_hsv": None
}

match_state = {
    "team1": 0, "team2": 0, "ball": False, 
    "comment": "Sistem hazır. Analiz bekleniyor."
}

global_frame = None
lock = threading.Lock()

vision = VisionEngine(config.TEAMS)
coach = VirtualCoach()

# 3. ARKA PLAN ANALİZ İŞÇİSİ (THREAD)
def analysis_worker(video_url, start_sec):
    global global_frame, control_state, match_state

    direct_url = get_direct_url(video_url)
    if not direct_url: return

    cap = cv2.VideoCapture(direct_url)
    cap.set(cv2.CAP_PROP_POS_MSEC, start_sec * 1000)

    match_logs = []
    frame_counter = 0
    control_state["running"] = True
    control_state["stop_requested"] = False

    print("Analiz Thread'i Başlatıldı!")

    while control_state["running"]:
        # A)KULLANICI DURDURDU MU?
        if control_state["stop_requested"]:
            match_state["comment"] = "Analiz sonlandırıldı."
            break

        # B)TOKEN SÜRESİ DOLDU MU?
        current_pos_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
        if control_state["end_time_sec"] > 0 and current_pos_sec >= control_state["end_time_sec"]:
            match_state["comment"] = "Süre doldu (Token Sınırı)."
            break

        # C)PAUSE VE SEEK KONTROLLERİ
        if control_state["paused"]:
            time.sleep(0.1)
            continue

        if control_state["seek_command"] != 0:
            new_pos = max(0, current_pos_sec + control_state["seek_command"]) * 1000
            cap.set(cv2.CAP_PROP_POS_MSEC, new_pos)
            control_state["seek_command"] = 0

        success, frame = cap.read()
        if not success: break

        # D)GÖRÜNTÜ İŞLEME
        if frame_counter % 3 == 0:
            #Renk Ayarları Uygula
            if control_state["team1_hsv"]:
                h, s, v = control_state["team1_hsv"]
                vision.teams["TEAM_1"]["LOWER"] = np.array([max(0, h-20), 50, 50])
                vision.teams["TEAM_1"]["UPPER"] = np.array([min(180, h+20), 255, 255])
                vision.teams["TEAM_1"]["NAME"] = control_state["team1_name"]
            
            if control_state["team2_hsv"]:
                h, s, v = control_state["team2_hsv"]
                vision.teams["TEAM_2"]["LOWER"] = np.array([max(0, h-20), 50, 50])
                vision.teams["TEAM_2"]["UPPER"] = np.array([min(180, h+20), 255, 255])
                vision.teams["TEAM_2"]["NAME"] = control_state["team2_name"]

            #AI Analizi
            stats = vision.process_frame(frame)
            
            match_state["team1"] = stats["team1_count"]
            match_state["team2"] = stats["team2_count"]
            match_state["ball"] = stats["ball"]
            
            #Koç Mantığı
            time_str = f"{int(current_pos_sec//60)}:{int(current_pos_sec%60):02d}"
            match_logs.append(f"Dk {time_str} | {stats['team1_name']}: {stats['team1_count']} | {stats['team2_name']}: {stats['team2_count']}")

            if len(match_logs) > 15:
                match_state["comment"] = f"[{time_str}] Oyun temposu analiz ediliyor..."
                match_logs = []

            # E)ÇIKTIYI GÜNCELLE
            with lock:
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    global_frame = buffer.tobytes()

        frame_counter += 1
        time.sleep(0.01)

    control_state["running"] = False
    cap.release()
    print("🛑 Analiz Thread'i Durdu.")

# --- VİDEO YAYINCISI ---
def stream_output():
    while True:
        with lock:
            if global_frame is None:
                time.sleep(0.1)
                continue
            frame_data = global_frame
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
        time.sleep(0.04)

# 4. ROTALAR
@app.route('/')
def home(): return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('email') == "admin@admin.com" and request.form.get('password') == "1234":
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard(): return render_template('dashboard.html')

@app.route('/video_feed')
def video_feed():
    return Response(stream_output(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data(): return jsonify(match_state)

@app.route('/get_balance', methods=['GET'])
def get_balance():
    return jsonify({"balance": get_user_tokens("admin@admin.com")})

@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.json
    cost = int(data.get('cost'))
    # URL'i JS'den alıyorum
    url = data.get('video_url') 

    balance = get_user_tokens("admin@admin.com")
    if balance < cost:
        return jsonify({"status": "error", "message": "Yetersiz Bakiye"}), 400

    update_user_tokens("admin@admin.com", -cost)
    
    control_state["team1_name"] = data.get("t1_name")
    control_state["team2_name"] = data.get("t2_name")
    
    #Renk Dönüşümü (JS RGB -> Python HSV)
    def rgb_to_hsv(rgb):
        if not rgb: return None
        c = np.uint8([[rgb]])
        hsv = cv2.cvtColor(c, cv2.COLOR_RGB2HSV)[0][0]
        return [int(hsv[0]), int(hsv[1]), int(hsv[2])]

    control_state["team1_hsv"] = rgb_to_hsv(data.get("t1_rgb"))
    control_state["team2_hsv"] = rgb_to_hsv(data.get("t2_rgb"))
    
    start_min = int(data.get("start_min"))
    control_state["end_time_sec"] = (start_min + int(data.get("duration"))) * 60
    
    #Thread Başlat
    t = threading.Thread(target=analysis_worker, args=(url, start_min * 60))
    t.daemon = True
    t.start()
    
    return jsonify({"status": "started"})

@app.route('/get_frame', methods=['POST'])
def get_frame():
    data = request.json
    direct = get_direct_url(data.get('url'))
    cap = cv2.VideoCapture(direct)
    cap.set(cv2.CAP_PROP_POS_MSEC, int(data.get('time_min', 2)) * 60 * 1000)
    success, frame = cap.read()
    cap.release()
    if success:
        _, buffer = cv2.imencode('.jpg', frame)
        import base64
        img_str = base64.b64encode(buffer).decode('utf-8')
        return jsonify({"status": "ok", "image": img_str})
    return jsonify({"status": "error"})

@app.route('/calculate_cost', methods=['POST'])
def calculate_cost():
    data = request.json
    try:
        cost = int(data.get('end', 10)) - int(data.get('start', 0))
    except: cost = 0
    return jsonify({"cost": cost, "balance": get_user_tokens(), "can_afford": get_user_tokens()>=cost, "max_minutes": get_user_tokens()})

@app.route('/stop_analysis', methods=['POST'])
def stop_analysis():
    control_state["stop_requested"] = True
    return jsonify({"status": "stopped"})

@app.route('/control_video', methods=['POST'])
def control_video():
    action = request.json.get('action')
    if action == 'pause': control_state["paused"] = True
    elif action == 'play': control_state["paused"] = False
    elif action == 'forward': control_state["seek_command"] = 30
    elif action == 'rewind': control_state["seek_command"] = -10
    return jsonify({"status": "ok", "paused": control_state["paused"]})

@app.route('/update_teams', methods=['POST'])
def update_teams():
    data = request.json
    control_state["team1_name"] = data.get('team1')
    control_state["team2_name"] = data.get('team2')
    return jsonify({"status": "updated"})

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET': return redirect(url_for('home', _anchor='contact'))
    return "Mesaj alındı"

@app.route('/register')
def register(): return redirect(url_for('home', _anchor='contact'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)