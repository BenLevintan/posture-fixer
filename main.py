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
            print("Error: Video stream interrupted.")
            break

        # Send the raw frame into the detector.
        # It will return the same frame, but with the skeleton drawn on it!
        frame = detector.find_and_draw_pose(frame)

        cv2.imshow('Posture Detection Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()