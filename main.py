import cv2
from camera_utils import get_working_camera
from pose_utils import PoseDetector # Import your new tool

def main():
    cap = get_working_camera()

    if cap is None:
        return

    print("Camera initialized. Press 'q' to quit.")

    # Initialize our pose detector object BEFORE the loop starts
    detector = PoseDetector()

    while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = detector.find_and_draw_pose(frame)
            
            # Get our true perpendicular distance
            slouch_distance = detector.get_posture_data()
            
            if slouch_distance is not None:
                # Print it so we can observe the math in real-time
                print(f"Distance from Line: {slouch_distance:.4f}")
                
                # If distance is > 0, the nose crossed the slanted shoulder line!
                # You might want to use something like > 0.05 to give yourself a tiny bit of grace room.
                if slouch_distance > 0.02: 
                    print("⚠️ BAD POSTURE DETECTED! ⚠️")

            cv2.imshow('Posture Detection Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()