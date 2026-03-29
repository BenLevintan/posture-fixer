import customtkinter as ctk
import cv2
from PIL import Image
import time
from camera_utils import get_working_camera
from pose_utils import PoseDetector

# Set the overall Apple-like aesthetic
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Options: "blue", "green", "dark-blue"

class PostureApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Posture Monitor")
        self.geometry("900x600")
        self.grid_columnconfigure(0, weight=1) # Video takes most space
        self.grid_columnconfigure(1, weight=0) # Controls panel

        # --- Backend Initialization ---
        self.cap = get_working_camera()
        if self.cap is None:
            print("Failed to initialize camera.")
            self.destroy()
            return
            
        self.cap.set(cv2.CAP_PROP_FPS, 10)
        self.detector = PoseDetector()
        
        # State Variables
        self.bad_posture_start_time = None
        self.frame_counter = 0
        self.cached_distance = None
        
        # --- Build UI Layout ---
        self.build_ui()

        # Start the video loop
        self.update_video_feed()

    def build_ui(self):
        # 1. Video Frame (Left Side)
        self.video_frame = ctk.CTkFrame(self, corner_radius=15)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # 2. Controls Panel (Right Side)
        self.control_panel = ctk.CTkFrame(self, width=300, corner_radius=15)
        self.control_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        # Title
        title = ctk.CTkLabel(self.control_panel, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(20, 30))

        # Sliders mapped to class variables (replacing your CONFIG dictionary)
        # Threshold Slider
        self.thresh_label = ctk.CTkLabel(self.control_panel, text="Slouch Sensitivity: 0.02", font=ctk.CTkFont(size=14))
        self.thresh_label.pack(anchor="w", padx=20)
        self.thresh_slider = ctk.CTkSlider(self.control_panel, from_=0.0, to=0.1, command=self.update_labels)
        self.thresh_slider.set(0.02)
        self.thresh_slider.pack(fill="x", padx=20, pady=(0, 20))

        # Delay Slider
        self.delay_label = ctk.CTkLabel(self.control_panel, text="Alert Delay: 1.5s", font=ctk.CTkFont(size=14))
        self.delay_label.pack(anchor="w", padx=20)
        self.delay_slider = ctk.CTkSlider(self.control_panel, from_=0.5, to=5.0, command=self.update_labels)
        self.delay_slider.set(1.5)
        self.delay_slider.pack(fill="x", padx=20, pady=(0, 20))

        # Status Label (Shows if you are slouching or not)
        self.status_label = ctk.CTkLabel(self.control_panel, text="Status: Good", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2ECC71") # Green
        self.status_label.pack(pady=40)

    def update_labels(self, _):
        """Updates text labels when sliders are moved."""
        self.thresh_label.configure(text=f"Slouch Sensitivity: {self.thresh_slider.get():.3f}")
        self.delay_label.configure(text=f"Alert Delay: {self.delay_slider.get():.1f}s")

    def update_video_feed(self):
            ret, frame = self.cap.read()

            if ret:
                self.frame_counter += 1
                
                # Decide if we run the heavy AI on this frame (1 out of every 2 frames)
                should_run_ai = (self.frame_counter % 2 == 0)

                # Pass the flag to the detector. 
                # It will draw the skeleton on EVERY frame, but only do the math on SOME frames!
                frame = self.detector.find_and_draw_pose(frame, run_ai=should_run_ai)
                
                # Only update our distance math when the AI actually ran
                if should_run_ai:
                    self.cached_distance = self.detector.get_posture_data()

                current_time = time.time()

                # Use our cached distance for the posture logic
                if self.cached_distance is not None:
                    if self.cached_distance > self.thresh_slider.get():
                        if self.bad_posture_start_time is None:
                            self.bad_posture_start_time = current_time
                        
                        elapsed_time = current_time - self.bad_posture_start_time
                        
                        if elapsed_time >= self.delay_slider.get():
                            self.status_label.configure(text="Status: BAD POSTURE", text_color="#E74C3C")
                            # TODO: Play Audio Alert Here!
                            
                    else:
                        self.bad_posture_start_time = None
                        self.status_label.configure(text="Status: Good", text_color="#2ECC71")

                # --- Convert Image for the UI ---
                color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(color_converted)
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(640, 480))
                self.video_label.configure(image=ctk_image)

            # Run again in 15 milliseconds
            self.after(15, self.update_video_feed)

    def on_closing(self):
        """Fires when the user clicks the 'X' to close the app."""
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = PostureApp()
    # Hook up the closing event to properly release the camera
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    # Start the GUI event loop
    app.mainloop()