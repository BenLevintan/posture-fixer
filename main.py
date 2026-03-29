# main.py
import cv2
import time
from camera_utils import get_working_camera
from pose_utils import PoseDetector

# --- CONFIGURATION DICTIONARY ---
CONFIG = {
    "diff_threshold": 0.0,  
    "camera_fps": 30,        
    "time_delay": 1.5,       
    "sample_rate": 1         # NEW: Only process 1 out of every x frames
}

def main():
    cap = get_working_camera()

    if cap is None:
        return

    cap.set(cv2.CAP_PROP_FPS, CONFIG["camera_fps"])
    print("Camera initialized. Press 'q' to quit.")

    detector = PoseDetector()
    
    # --- STATE VARIABLES ---
    bad_posture_start_time = None 
    frame_counter = 0  # NEW: Keep track of how many frames have passed

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Video stream interrupted.")
            break

        frame_counter += 1

        # NEW: Only run the heavy AI and math if it is the "nth" frame
        if frame_counter % CONFIG["sample_rate"] == 0:
            
            # The heavy lifting
            frame = detector.find_and_draw_pose(frame)
            slouch_distance = detector.get_posture_data()
            
            current_time = time.time()

            if slouch_distance is not None:
                if slouch_distance > CONFIG["diff_threshold"]:
                    if bad_posture_start_time is None:
                        bad_posture_start_time = current_time
                        print("Posture degrading... starting timer.")
                    
                    elapsed_time = current_time - bad_posture_start_time
                    
                    if elapsed_time >= CONFIG["time_delay"]:
                        print(f"⚠️ ALERT! Bad posture for {elapsed_time:.1f} seconds! ⚠️")
                        
                else:
                    if bad_posture_start_time is not None:
                        print("Posture corrected. Timer reset.")
                        bad_posture_start_time = None

        # Display the frame (Note: on skipped frames, the skeleton won't be drawn!)
        cv2.imshow('Posture Detection Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()