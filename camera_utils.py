import cv2

def get_working_camera():

    print("Attempting to connect to external cam...")
    cap = cv2.VideoCapture(1)

    if cap.isOpened():
        ret, test_frame = cap.read()
        if ret:
            print("Using external cam.")
            return cap
        
    cap.release()

    print("Failed to connect to an external cam, falling back to index 0...")
    cap = cv2.VideoCapture(0)    

    if cap.isOpened():
        ret, test_frame = cap.read()
        if ret:
            print("Using index 0 cam.")
            return cap
        
    cap.release()
    print("Error: Could not find any working cameras.")
    return None