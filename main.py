import cv2

from camera_utils import get_working_camera

def main():
    # Call our new function to get the correct camera
    cap = get_working_camera()

    # If it returned None, we can't proceed. Exit the program.
    if cap is None:
        return

    print("Camera initialized. Press 'q' to quit.")

    # The video loop remains exactly the same
    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Video stream interrupted.")
            break

        cv2.imshow('Posture Detection Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()