from fer import FER
import cv2
import numpy as np

class EmotionModel:
    def __init__(self):
        print("EmotionModel: Initializing FER...")
        # Initialize FER with mtcnn=True for better face detection if needed, 
        # or simplified. MTCNN is slower but accurate. 
        # For real-time, maybe use default opencv cascade in FER or just pass face crop.
        try:
            self.detector = FER(mtcnn=False) # Use OpenCV Haarcascade for speed
            print("EmotionModel: FER Initialized.")
        except Exception as e:
            print(f"Warning: FER initialization failed: {e}")
            self.detector = None

    def predict(self, frame, face_box=None):
        if self.detector is None:
            return "neutral", 0.0

        # FER expects full frame. If face_box provided, clearer.
        # But FER has internal detection. 
        # To speed up, if we already have face from MediaPipe, we should crop and pass.
        # However, FER `detect_emotions` takes an image.
        
        try:
            if face_box:
                x, y, w, h = face_box
                # Ensure box is within frame
                H, W, _ = frame.shape
                x = max(0, x); y = max(0, y)
                w = min(W-x, w); h = min(H-y, h)
                face_img = frame[y:y+h, x:x+w]
                if face_img.size == 0: return "neutral", 0.0
                
                # FER top_emotion returns (emotion, score)
                emotion, score = self.detector.top_emotion(face_img)
            else:
                emotion, score = self.detector.top_emotion(frame)
                
            return emotion if emotion else "neutral", score if score else 0.0
        except Exception as e:
            print(f"Emotion prediction error: {e}")
            return "neutral", 0.0
