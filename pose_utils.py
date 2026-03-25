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

    def find_and_draw_pose(self, frame):
        """Processes the frame, finds the pose, and draws the skeleton."""
        
        # CRITICAL STEP: Color Conversion
        # OpenCV reads images in BGR (Blue, Green, Red) format.
        # MediaPipe expects images in RGB (Red, Green, Blue) format.
        # We must convert the color space before handing it to the AI.
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Pass the RGB image to the model to find the body landmarks
        self.results = self.pose.process(img_rgb)

        # If the AI found a body (landmarks), draw them on the ORIGINAL BGR frame
        if self.results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame, 
                self.results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS # This draws the lines connecting the joints
            )
            
        return frame