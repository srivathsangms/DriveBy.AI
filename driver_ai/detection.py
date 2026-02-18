
import cv2
import mediapipe as mp
import time
import threading
import pygame
import numpy as np
import requests
import json
import os
from fatigue_engine import FatigueEngine
from emotion_model import EmotionModel
from utils import calculate_ear # optional if needed directly

class DriverMonitor:
    def __init__(self, camera_index=0):
        print("DriverMonitor: Initializing...")
        self.cap = cv2.VideoCapture(camera_index)
        
        print("DriverMonitor: Loading MediaPipe...")
        # MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Models
        self.fatigue_engine = FatigueEngine()
        self.emotion_model = EmotionModel()
        
        # State
        self.running = True
        self.alert_active = False
        self.current_log = {}
        
        # Audio
        try:
            pygame.mixer.init()
            # Generate a beep sound
            self.alert_sound = self._generate_beep()
        except Exception as e:
            print(f"Warning: Audio initialization failed: {e}")
            self.alert_sound = None
        
        # API config
        self.API_URL = os.getenv("API_URL", "http://localhost:8000")
        self.auth_token = None # Needs login
        
    def _generate_beep(self):
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Generate sine wave
        tone = np.sin(frequency * t * 2 * np.pi)
        # Normalize to 16-bit range
        audio = (tone * 32767).astype(np.int16)
        # Stereo
        audio = np.column_stack((audio, audio))
        
        return pygame.sndarray.make_sound(audio)

    def login(self, email, password):
        try:
            print(f"DriverMonitor: Logging in as {email}...")
            res = requests.post(f"{self.API_URL}/auth/login", json={"email": email, "password": password})
            if res.status_code == 200:
                self.auth_token = res.json()["access_token"]
                print("Logged in successfully.")
                return True
            else:
                print(f"Login failed: {res.text}")
                return False
        except Exception as e:
            print(f"Login connection error: {e}")
            return False

    def send_log(self, data):
        if not self.auth_token: return
        
        def _send():
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                requests.post(f"{self.API_URL}/logs/upload", json=data, headers=headers)
            except Exception as e:
                pass # Silent fail for logs
                
        threading.Thread(target=_send).start()

    def run(self):
        print("DriverMonitor: Starting run loop...")
        prev_time = 0
        
        if not self.cap.isOpened():
            print("DriverMonitor Error: Camera not opened.")
            return

        consecutive_failures = 0
        while self.running and self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                consecutive_failures += 1
                if consecutive_failures > 10:
                    print("Camera failure limit reached. Exiting.")
                    break
                continue
            consecutive_failures = 0

            # Performance optimization
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(image_rgb)
            image.flags.writeable = True

            frame_h, frame_w, _ = image.shape
            
            face_box = None

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # Calculate Face Box for Emotion
                    x_min, y_min = frame_w, frame_h
                    x_max, y_max = 0, 0
                    for lm in face_landmarks.landmark:
                        x, y = int(lm.x * frame_w), int(lm.y * frame_h)
                        if x < x_min: x_min = x
                        if x > x_max: x_max = x
                        if y < y_min: y_min = y
                        if y > y_max: y_max = y
                    face_box = (x_min, y_min, x_max - x_min, y_max - y_min)

                    # Fatigue Engine
                    fatigue_data = self.fatigue_engine.process_landmarks(face_landmarks, (frame_h, frame_w, 3))
                    
                    # Emotion Engine
                    emotion, emotion_score = self.emotion_model.predict(image, face_box)
                    
                    # Composite Logic
                    total_score = fatigue_data["fatigue_partial_score"]
                    if emotion in ["nervous", "fear", "sad", "angry"]:
                        total_score += 10
                    
                    final_score = min(100, total_score)
                    
                    # Alert
                    if final_score > 80:
                        self.alert_active = True
                        if self.alert_sound and not pygame.mixer.get_busy():
                            self.alert_sound.play()
                        cv2.rectangle(image, (0, 0), (frame_w, frame_h), (0, 0, 255), 10)
                        cv2.putText(image, "DROWSINESS ALERT!", (50, frame_h // 2), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    else:
                        self.alert_active = False

                    # Prepare Log
                    log_data = {
                        "fatigue_score": float(final_score),
                        "emotion": emotion,
                        "drowsy_status": fatigue_data["drowsy"] # Only report eyes for "Eye Status"
                    }
                    self.current_log = log_data
                    
                    # Send Log (throttled)
                    if time.time() - prev_time > 1.0:
                        self.send_log(log_data)
                        prev_time = time.time()

                    # Visualization
                    cv2.putText(image, f"Score: {final_score:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(image, f"Emotion: {emotion}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    cv2.putText(image, f"EAR: {fatigue_data['ear']:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    cv2.putText(image, f"MAR: {fatigue_data['mar']:.2f}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            cv2.imshow('DriveBy.AI Monitor', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor = DriverMonitor()
    monitor.login("testdriver@gmail.com", "password123") 
    monitor.run()
