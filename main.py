import cv2
import numpy as np
import config
import datetime
import time
import sys
from video_stream import get_direct_url
from vision_ai import VisionEngine
from coach_ai import VirtualCoach

# --- GLOBAL VARIABLES ---
selected_hsv = None
picking_mode = False

# --- STATISTICS DATABASE ---
STATS = {
    "team1_frames": 0,
    "team2_frames": 0,
    "total_frames": 0,
    "last_coach_comment": "Waiting for analysis...",
    "ball_detected_count": 0
}

def mouse_callback(event, x, y, flags, param):
    """Captures mouse click and gets HSV color."""
    global selected_hsv, picking_mode
    if event == cv2.EVENT_LBUTTONDOWN and picking_mode:
        frame = param
        pixel_bgr = frame[y, x]
        pixel_hsv = cv2.cvtColor(np.uint8([[pixel_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
        selected_hsv = pixel_hsv
        print(f"\n✅ Color Detected! (HSV: {selected_hsv})")
        picking_mode = False

def setup_teams(cap):
    """Interactive Team Setup Wizard."""
    global picking_mode, selected_hsv
    team_settings = {}
    
    print("Capturing video frame...")
    for _ in range(30): cap.read()
    
    ret, frame = cap.read()
    if not ret:
        print("Error reading video!")
        return None

    window_name = "SETUP - Click on Jersey"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback, frame)

    for i in range(1, 3):
        print(f"\n--- TEAM {i} SELECTION ---")
        print(f"Please click on the jersey of TEAM {i}...")
        picking_mode = True
        selected_hsv = None
        
        while selected_hsv is None:
            text_frame = frame.copy()
            cv2.putText(text_frame, f"CLICK ON TEAM {i} JERSEY", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow(window_name, text_frame)
            if cv2.waitKey(10) == 27: sys.exit() # ESC
        
        hue = selected_hsv[0]
        lower = np.array([max(0, hue-20), 50, 50]) 
        upper = np.array([min(180, hue+20), 255, 255])
        
        # Hide window temporarily for input
        cv2.imshow(window_name, np.zeros_like(frame)) 
        name = input(f"Enter Name for Team {i}: ")
        
        team_settings[f"TEAM_{i}"] = {"NAME": name, "LOWER": lower, "UPPER": upper}
        
    cv2.destroyAllWindows()
    return team_settings

def draw_dashboard(t1_name, t1_count, t2_name, t2_count, ball_status, time_str, remaining_str):
    """Draws the Statistics Dashboard on a black background."""
    
    board = np.zeros((500, 600, 3), dtype=np.uint8)
    
    # Headers
    cv2.putText(board, "LIVE MATCH ANALYTICS", (180, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.line(board, (20, 50), (580, 50), (100, 100, 100), 2)
    
    # Time Info
    cv2.putText(board, f"MATCH TIME: {time_str}", (30, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
    cv2.putText(board, f"REMAINING: {remaining_str}", (350, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 1)

    # Team Scores (Visible Players)
    # Team 1
    cv2.putText(board, f"{t1_name}", (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(board, f"Visible: {t1_count}", (30, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
    
    # Team 2
    cv2.putText(board, f"{t2_name}", (350, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    cv2.putText(board, f"Visible: {t2_count}", (350, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
    
    # Possession Bar
    total_seen = STATS['team1_frames'] + STATS['team2_frames'] + 1 
    t1_ratio = int((STATS['team1_frames'] / total_seen) * 400)
    
    cv2.putText(board, "POSSESSION (Visual estimate)", (150, 230), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.rectangle(board, (100, 250), (500, 270), (50, 50, 50), -1)
    cv2.rectangle(board, (100, 250), (100 + t1_ratio, 270), (0, 255, 255), -1)
    cv2.line(board, (300, 245), (300, 275), (255, 255, 255), 2)
    
    # Ball Status
    color = (0, 255, 0) if "VISIBLE" in ball_status else (0, 0, 255)
    cv2.putText(board, f"BALL: {ball_status}", (180, 320), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Coach Comments
    cv2.putText(board, "LATEST AI COACH COMMENT:", (30, 380), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
    y0, dy = 410, 20
    for i, line in enumerate(STATS['last_coach_comment'].split('\n')):
        if len(line) > 55: line = line[:55] + "..."
        y = y0 + i * dy
        cv2.putText(board, line, (30, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("LIVE ANALYTICS DASHBOARD", board)

def write_to_report(text):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    with open("Match_Report.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {text}\n")

def main():
    print("\n--- FOOTBALL ANALYSIS SYSTEM STARTING ---")
    
    stream_url = get_direct_url(config.VIDEO_URL)
    if not stream_url: return

    cap = cv2.VideoCapture(stream_url)
    cap.set(cv2.CAP_PROP_POS_MSEC, config.START_TIME_SEC * 1000)
    
    # Get Total Duration
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    total_seconds = total_frames / fps if fps > 0 else 0
    
    # 1. SETUP WIZARD
    team_config = setup_teams(cap)
    if not team_config: return

    # Init Modules
    vision = VisionEngine(team_config)
    coach = VirtualCoach()
    
    match_logs = []
    frame_counter = 0
    last_analysis_time = time.time()
    
    write_to_report(f"ANALYSIS STARTED: {team_config['TEAM_1']['NAME']} vs {team_config['TEAM_2']['NAME']}")
    print("\nAnalysis started. Check the 'LIVE ANALYTICS DASHBOARD' window.")

    while True:
        success, frame = cap.read()
        if not success: break

        if frame_counter % 5 == 0: 
            stats = vision.process_frame(frame)
            
            # Update Stats
            if stats['team1_count'] > stats['team2_count']: STATS['team1_frames'] += 1
            elif stats['team2_count'] > stats['team1_count']: STATS['team2_frames'] += 1
            if stats['ball']: STATS['ball_detected_count'] += 1
            STATS['total_frames'] += 1
            
            # Time Calc
            current_sec = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            mins, secs = int(current_sec // 60), int(current_sec % 60)
            time_str = f"{mins}:{secs:02d}"
            
            if total_seconds > 0:
                rem_sec = max(0, total_seconds - current_sec)
                rem_str = f"{int(rem_sec//60)}:{int(rem_sec%60):02d}"
            else:
                rem_str = "Live"

            ball_str = "VISIBLE" if stats['ball'] else "LOST"

            # 1. LOGGING
            log = f"Min {time_str} | {stats['team1_name']}: {stats['team1_count']} | {stats['team2_name']}: {stats['team2_count']} | Ball: {ball_str}"
            match_logs.append(log)
            
            # 2. UPDATE DASHBOARD
            draw_dashboard(
                team_config['TEAM_1']['NAME'], stats['team1_count'],
                team_config['TEAM_2']['NAME'], stats['team2_count'],
                ball_str, time_str, rem_str
            )

        frame_counter += 1

        # --- AI COACH AUTO-COMMENT (Every 60s) ---
        if (time.time() - last_analysis_time > 60) and len(match_logs) > 10:
            print(f"🤖 [{time_str}] Coach is analyzing...")
            comment = coach.analyze_game_data(match_logs)
            
            STATS['last_coach_comment'] = comment
            write_to_report(f"MIN {time_str} - {comment}")
            
            match_logs = []
            last_analysis_time = time.time()

        # Keyboard Controls
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): 
            write_to_report("ANALYSIS STOPPED.")
            print("Report saved: Match_Report.txt")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()