import cv2
import time  # We need this to track our delay
from camera_utils import get_working_camera
from pose_utils import PoseDetector

# --- CONFIGURATION DICTIONARY ---
CONFIG = {
    "diff_threshold": 0.00,  # How far the nose crosses the line before it's "bad"
    "camera_fps": 10,        # Target camera frame rate (saves CPU/Battery)
    "time_delay": 2.0        # Seconds of continuous bad posture before alert
}

def main():
    cap = get_working_camera()

    if cap is None:
        return

    # Attempt to limit the hardware frame rate to save resources
    cap.set(cv2.CAP_PROP_FPS, CONFIG["camera_fps"])

    print("Camera initialized. Press 'q' to quit.")

    detector = PoseDetector()
    
    # --- STATE VARIABLES ---
    # We use this to remember exactly when the bad posture started
    bad_posture_start_time = None 

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Video stream interrupted.")
            break

        frame = detector.find_and_draw_pose(frame)
        slouch_distance = detector.get_posture_data()
        
        # Get the exact time of the current frame
        current_time = time.time()

        if slouch_distance is not None:
            # 1. Check if the posture is bad based on our config threshold
            if slouch_distance > CONFIG["diff_threshold"]:
                
                # If this is the FIRST frame of bad posture, start the stopwatch
                if bad_posture_start_time is None:
                    bad_posture_start_time = current_time
                    print("Posture degrading... starting timer.")
                
                # Calculate how long we have been slouching
                elapsed_time = current_time - bad_posture_start_time
                
                # 2. Check if we've been slouching longer than our config delay
                if elapsed_time >= CONFIG["time_delay"]:
                    print(f"⚠️ ALERT! Bad posture for {elapsed_time:.1f} seconds! ⚠️")
                    # (We will trigger the actual audio sound here!)
                    
            else:
                # 3. Posture is GOOD! 
                # If the timer was running, reset it back to None.
                if bad_posture_start_time is not None:
                    print("Posture corrected. Timer reset.")
                    bad_posture_start_time = None

        cv2.imshow('Posture Detection Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()