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
            
            # Get the math for our custom angle!
            nose_y, shoulder_line_y = detector.get_posture_data()
            
            if nose_y is not None and shoulder_line_y is not None:
                # Calculate the difference. 
                # If difference is positive, the nose is BELOW the shoulder line (slouching!)
                difference = nose_y - shoulder_line_y
                
                # Print it so you can see the data stream
                print(f"Nose Y: {nose_y:.3f} | Shoulder Line Y: {shoulder_line_y:.3f} | Diff: {difference:.3f}")

            cv2.imshow('Posture Detection Feed', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()