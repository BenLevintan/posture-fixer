# pose_utils.py
import cv2
import mediapipe as mp
import math # Make sure to add this at the top!

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,       
            model_complexity=1,            
            min_detection_confidence=0.5,  
            min_tracking_confidence=0.5    
        )

    def find_and_draw_pose(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)

        if self.results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame, 
                self.results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
        return frame

    def get_posture_data(self):
        """Calculates the perpendicular distance from the nose to the shoulder line."""
        if self.results and self.results.pose_landmarks:
            landmarks = self.results.pose_landmarks.landmark
            
            # Extract specific landmarks
            nose = landmarks[0]
            l_shoulder = landmarks[11]
            r_shoulder = landmarks[12]
            
            # Step 1: Create a vector representing the shoulder line (Right to Left)
            dx = l_shoulder.x - r_shoulder.x
            dy = l_shoulder.y - r_shoulder.y
            
            # Step 2: Create a vector from the Right Shoulder to the Nose
            nx = nose.x - r_shoulder.x
            ny = nose.y - r_shoulder.y
            
            # Step 3: Calculate the physical length of the shoulder line
            line_length = math.sqrt(dx**2 + dy**2)
            
            # Prevent division by zero crash if shoulders somehow perfectly overlap
            if line_length == 0:
                return None
                
            # Step 4: Calculate signed perpendicular distance using the cross product
            distance = (dx * ny - dy * nx) / line_length
            
            return distance
            
        return None