import cv2
import mediapipe as mp
import math

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,       
            model_complexity=0,
            min_detection_confidence=0.5,  
            min_tracking_confidence=0.5    
        )
        self.results = None

    def find_and_draw_pose(self, frame, run_ai=True):
        if run_ai:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.results = self.pose.process(img_rgb)

        if self.results and self.results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame, 
                self.results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS
            )
            
        return frame

    def get_posture_data(self):
        """Calculates the max distance from either mouth corner to the shoulder line."""
        if self.results and self.results.pose_landmarks:
            landmarks = self.results.pose_landmarks.landmark
            
            left_mouth = landmarks[9]
            right_mouth = landmarks[10]
            
            l_shoulder = landmarks[11]
            r_shoulder = landmarks[12]
            
            dx = l_shoulder.x - r_shoulder.x
            dy = l_shoulder.y - r_shoulder.y
            
            line_length = math.sqrt(dx**2 + dy**2)
            
            if line_length == 0:
                return None
                
            lm_x = left_mouth.x - r_shoulder.x
            lm_y = left_mouth.y - r_shoulder.y
            left_distance = (dx * lm_y - dy * lm_x) / line_length
            
            rm_x = right_mouth.x - r_shoulder.x
            rm_y = right_mouth.y - r_shoulder.y
            right_distance = (dx * rm_y - dy * rm_x) / line_length
            
            return max(left_distance, right_distance)
            
        return None