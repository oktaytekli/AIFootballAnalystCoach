from ultralytics import YOLO
import cv2
import numpy as np

class VisionEngine:
    def __init__(self, team_config):
        print("Vision Engine (TRACKING MODE) Loading...")
        # Using Small model for better detection
        self.model = YOLO('yolov8s.pt') 
        self.teams = team_config
        
        # Player Memory (ID Tracking)
        self.track_history = {}
        
        # Ball Memory (Hysteresis)
        self.ball_memory = 0
        self.MAX_MEMORY = 20

    def detect_team_color(self, image_crop):
        """Determines the team name based on the dominant color of the crop."""
        if image_crop.size == 0: return None

        hsv_crop = cv2.cvtColor(image_crop, cv2.COLOR_BGR2HSV)
        
        # Team 1 Check
        mask1 = cv2.inRange(hsv_crop, np.array(self.teams["TEAM_1"]["LOWER"]), np.array(self.teams["TEAM_1"]["UPPER"]))
        # Team 2 Check
        mask2 = cv2.inRange(hsv_crop, np.array(self.teams["TEAM_2"]["LOWER"]), np.array(self.teams["TEAM_2"]["UPPER"]))
        
        count1 = cv2.countNonZero(mask1)
        count2 = cv2.countNonZero(mask2)
        total = image_crop.shape[0] * image_crop.shape[1]
        
        # Tolerance: At least 3% pixel match
        if count1 > count2 and count1 > (total * 0.03):
            return self.teams["TEAM_1"]["NAME"]
        elif count2 > count1 and count2 > (total * 0.03):
            return self.teams["TEAM_2"]["NAME"]
        else:
            return None

    def process_frame(self, frame):
        # Tracking enabled (persist=True)
        # Using 1280imgsz and low conf (0.15) for small ball detection
        results = self.model.track(
            frame, 
            persist=True, 
            classes=[0, 32], 
            tracker="bytetrack.yaml",
            verbose=False,
            conf=0.15,
            imgsz=1280
        )
        
        boxes = results[0].boxes
        if boxes.id is None: 
            ids = []
        else: 
            ids = boxes.id.int().cpu().tolist()
            
        cls_list = boxes.cls.int().cpu().tolist()
        
        team1_count = 0
        team2_count = 0
        current_ball_detected = False

        for i, box in enumerate(boxes.xyxy):
            cls = cls_list[i]
            
            # Person (Class 0)
            if cls == 0 and len(ids) > i:
                player_id = ids[i]
                
                # Check memory first
                if player_id in self.track_history:
                    team_name = self.track_history[player_id]
                else:
                    # New player, check color
                    x1, y1, x2, y2 = map(int, box)
                    h = y2 - y1
                    # Crop upper body
                    crop = frame[y1+int(h*0.1):y1+int(h*0.5), x1:x2]
                    
                    team_name = self.detect_team_color(crop)
                    if team_name:
                        self.track_history[player_id] = team_name
                
                if team_name == self.teams["TEAM_1"]["NAME"]:
                    team1_count += 1
                elif team_name == self.teams["TEAM_2"]["NAME"]:
                    team2_count += 1

            # Ball (Class 32)
            elif cls == 32:
                current_ball_detected = True

        # Ball Memory Logic
        if current_ball_detected:
            self.ball_memory = self.MAX_MEMORY
            final_ball = True
        else:
            if self.ball_memory > 0:
                self.ball_memory -= 1
                final_ball = True
            else:
                final_ball = False

        stats = {
            "team1_name": self.teams["TEAM_1"]["NAME"],
            "team1_count": team1_count,
            "team2_name": self.teams["TEAM_2"]["NAME"],
            "team2_count": team2_count,
            "ball": final_ball
        }
        return stats