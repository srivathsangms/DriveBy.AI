from utils import calculate_ear, calculate_mar, get_head_pose
import time
import numpy as np
import cv2
class FatigueEngine:
    def __init__(self):
        # Config Thresholds
        self.EYE_AR_THRESH = 0.20
        self.EYE_AR_CONSEC_FRAMES = 20
        self.MAR_THRESH = 0.60
        self.YAWN_FRAMES = 20
        
        # Counters
        self.counter_eyes = 0
        self.counter_yawn = 0
        self.total_yawns = 0
        
        self.start_time = time.time()
        self.yawn_frequency = 0
        
        # Tracking history for weighted score
        self.eye_closed_duration = 0
        
    def process_landmarks(self, face_landmarks, frame_shape):
        # MediaPipe landmarks to numpy array
        h, w, c = frame_shape
        landmarks = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])
        
        # EAR
        # Left Eye: 33 (P1), 160 (P2), 158 (P3), 133 (P4), 153 (P5), 144 (P6)
        left_eye_indices = [33, 160, 158, 133, 153, 144]
        # Right Eye: 362 (P1), 385 (P2), 387 (P3), 263 (P4), 373 (P5), 380 (P6)
        right_eye_indices = [362, 385, 387, 263, 373, 380]
        
        left_ear = calculate_ear(landmarks[left_eye_indices])
        right_ear = calculate_ear(landmarks[right_eye_indices])
        avg_ear = (left_ear + right_ear) / 2.0
        
        # MAR (Mouth Aspect Ratio)
        # Vertical: Upper Lip (13) - Lower Lip (14)
        # Horizontal: Left Corner (61) - Right Corner (291)
        # Indices: 13, 14, 61, 291
        
        # Using specific MP indices for MAR:
        mar = calculate_mar(
            landmarks[13],  # Top
            landmarks[14],  # Bottom
            landmarks[61],  # Left
            landmarks[291]  # Right
        )
        
        # Fatigue Logic
        drowsy = False
        yawn = False
        
        # Eyes
        if avg_ear < self.EYE_AR_THRESH:
            self.counter_eyes += 1
            if self.counter_eyes >= self.EYE_AR_CONSEC_FRAMES:
                drowsy = True
                self.eye_closed_duration += 1 # Frame count
        else:
            self.counter_eyes = 0
            self.eye_closed_duration = max(0, self.eye_closed_duration - 1)
            
        # Yawn
        if mar > self.MAR_THRESH:
            self.counter_yawn += 1
            if self.counter_yawn >= self.YAWN_FRAMES:
                yawn = True
                if self.counter_yawn == self.YAWN_FRAMES: # Count once per yawn
                    self.total_yawns += 1
        else:
            self.counter_yawn = 0
            
        # Head Pose (Tilt)
        rot_vec, trans_vec, cam_matrix, dist_coeffs = get_head_pose(landmarks, frame_shape)
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        
        # angles: pitch, yaw, roll
        pitch = angles[0] * 360
        yaw = angles[1] * 360
        roll = angles[2] * 360
        
        head_tilt = False
        if abs(pitch) > 20 or abs(roll) > 20: # Looking down or tilted
            head_tilt = True
            
        # Composite Score Calculation (0-100)
        # Weights Adjusted for >80 Alert Threshold:
        # Eye (Closed): 0.85 -> 85 score (Triggers Alert)
        # Yawn: 0.10 
        # Head Tilt: 0.05
        
        eye_factor = 1.0 if avg_ear < self.EYE_AR_THRESH else 0.0
        yawn_factor = 1.0 if mar > self.MAR_THRESH else 0.0
        head_tilt_factor = 1.0 if head_tilt else 0.0
        
        # Partial score (excluding emotion)
        partial_score = (eye_factor * 0.85 + yawn_factor * 0.10 + head_tilt_factor * 0.05) * 100
        
        return {
            "drowsy": drowsy,
            "yawn": yawn,
            "head_tilt": head_tilt,
            "ear": avg_ear,
            "mar": mar,
            "fatigue_partial_score": min(100, partial_score) # Max 100
        }
