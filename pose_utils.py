import cv2
import mediapipe as mp

class PoseDetector:
    def __init__(self):
        # Initialize the MediaPipe Pose module
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        
        # Setup the pose model with standard parameters
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,       # False means it treats the feed as a video, tracking motion
            model_complexity=1,            # 0 is fastest, 2 is most accurate. 1 is a good middle ground.
            min_detection_confidence=0.5,  # How confident the AI must be to initially find a person
            min_tracking_confidence=0.5    # How confident it must be to keep tracking them
        )

import cv2
import mediapipe as mp

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
        """Extracts the specific Y coordinates needed for the top-down angle."""
        if self.results and self.results.pose_landmarks:
            landmarks = self.results.pose_landmarks.landmark
            
            # MediaPipe landmarks give values from 0.0 to 1.0 (percentages of the screen)
            # Landmark 0 = Nose, 11 = Left Shoulder, 12 = Right Shoulder
            nose_y = landmarks[0].y
            l_shoulder_y = landmarks[11].y
            r_shoulder_y = landmarks[12].y
            
            # Calculate the "Shoulder Line" (average Y of both shoulders)
            shoulder_line_y = (l_shoulder_y + r_shoulder_y) / 2
            
            # Return these values so we can use them in main.py
            return nose_y, shoulder_line_y
            
        return None, None
            
        return frame