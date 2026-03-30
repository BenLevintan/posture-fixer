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
        # Only do the heavy AI math if the flag is True
        if run_ai:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.results = self.pose.process(img_rgb)

        # Draw the skeleton whether we just found it, OR we are using the cached results!
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
            
            # Extract specific landmarks (9 is Left Mouth, 10 is Right Mouth)
            left_mouth = landmarks[9]
            right_mouth = landmarks[10]
            
            l_shoulder = landmarks[11]
            r_shoulder = landmarks[12]
            
            # Step 1: Create a vector representing the shoulder line (Right to Left)
            dx = l_shoulder.x - r_shoulder.x
            dy = l_shoulder.y - r_shoulder.y
            
            # Calculate the physical length of the shoulder line
            line_length = math.sqrt(dx**2 + dy**2)
            
            if line_length == 0:
                return None
                
            # Step 2: Calculate distance for the Left Mouth Corner
            lm_x = left_mouth.x - r_shoulder.x
            lm_y = left_mouth.y - r_shoulder.y
            left_distance = (dx * lm_y - dy * lm_x) / line_length
            
            # Step 3: Calculate distance for the Right Mouth Corner
            rm_x = right_mouth.x - r_shoulder.x
            rm_y = right_mouth.y - r_shoulder.y
            right_distance = (dx * rm_y - dy * rm_x) / line_length
            
            # Step 4: Return whichever distance is greater (further down the screen)
            return max(left_distance, right_distance)
            
        return None