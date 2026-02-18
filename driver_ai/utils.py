import numpy as np
import cv2

def calculate_ear(eye_landmarks):
    # Euclidean distance between vertical eye landmarks
    A = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    B = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    # Euclidean distance between horizontal eye landmarks
    C = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    
    if C < 1e-6: # Avoid division by zero
        return 0.0
        
    ear = (A + B) / (2.0 * C)
    return max(0.0, min(ear, 0.5)) # Clamp to 0.0 - 0.5

def calculate_mar(top, bottom, left, right):
    # Expects numpy arrays for points
    # Vertical distance
    h = np.linalg.norm(top - bottom)
    # Horizontal distance
    w = np.linalg.norm(left - right)
    
    if w < 1e-6:
        return 0.0
        
    mar = h / w
    return max(0.0, min(mar, 1.5)) # Clamp to 0.0 - 1.5

def get_head_pose(shape, size):
    # 2D image points. If you change the image, you need to change the vector
    image_points = np.array([
        shape[1],     # Nose tip
        shape[152],   # Chin
        shape[226],   # Left eye left corner
        shape[446],   # Right eye right corner
        shape[57],    # Left Mouth corner
        shape[287]    # Right mouth corner
    ], dtype="double")

    # 3D model points.
    model_points = np.array([
        (0.0, 0.0, 0.0),             # Nose tip
        (0.0, -330.0, -65.0),        # Chin
        (-225.0, 170.0, -135.0),     # Left eye left corner
        (225.0, 170.0, -135.0),      # Right eye right corner
        (-150.0, -150.0, -125.0),    # Left Mouth corner
        (150.0, -150.0, -125.0)      # Right mouth corner
    ])

    # Camera internals
    focal_length = size[1]
    center = (size[1]/2, size[0]/2)
    camera_matrix = np.array(
        [[focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]], dtype = "double"
    )

    dist_coeffs = np.zeros((4,1)) # Assuming no lens distortion
    
    (success, rotation_vector, translation_vector) = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)

    return rotation_vector, translation_vector, camera_matrix, dist_coeffs
