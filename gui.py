import customtkinter as ctk
import cv2
from PIL import Image
import time
import numpy as np
import sounddevice as sd  # Used to generate our synthetic beep
from camera_utils import get_working_camera
from pose_utils import PoseDetector

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PostureApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Posture Monitor")
        self.geometry("900x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.cap = get_working_camera()
        if self.cap is None:
            print("Failed to initialize camera.")
            self.destroy()
            return
            
        self.cap.set(cv2.CAP_PROP_FPS, 10)
        self.detector = PoseDetector()
        
        # --- State Variables ---
        self.bad_posture_start_time = None
        self.frame_counter = 0
        self.cached_distance = None
        self.last_beep_time = 0  # NEW: Keeps track of when we last beeped

        self.build_ui()
        self.update_video_feed()

    def build_ui(self):
        # 1. Video Frame
        self.video_frame = ctk.CTkFrame(self, corner_radius=15)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # 2. Controls Panel
        self.control_panel = ctk.CTkFrame(self, width=300, corner_radius=15)
        self.control_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        title = ctk.CTkLabel(self.control_panel, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=(20, 30))

        # Sensitivity Slider
        self.thresh_label = ctk.CTkLabel(self.control_panel, text="Slouch Sensitivity: 0.02", font=ctk.CTkFont(size=14))
        self.thresh_label.pack(anchor="w", padx=20)
        self.thresh_slider = ctk.CTkSlider(self.control_panel, from_=0.0, to=0.1, command=self.update_labels)
        self.thresh_slider.set(0.02)
        self.thresh_slider.pack(fill="x", padx=20, pady=(0, 20))

        # Delay Slider (NOW STARTS AT 0.0)
        self.delay_label = ctk.CTkLabel(self.control_panel, text="Alert Delay: 1.5s", font=ctk.CTkFont(size=14))
        self.delay_label.pack(anchor="w", padx=20)
        self.delay_slider = ctk.CTkSlider(self.control_panel, from_=0.0, to=5.0, command=self.update_labels)
        self.delay_slider.set(1.5)
        self.delay_slider.pack(fill="x", padx=20, pady=(0, 20))

        # Status Label
        self.status_label = ctk.CTkLabel(self.control_panel, text="Status: Good", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2ECC71")
        self.status_label.pack(pady=(40, 5))

        # NEW: Warning Icon Label (starts empty)
        self.warning_label = ctk.CTkLabel(self.control_panel, text="", font=ctk.CTkFont(size=50))
        self.warning_label.pack(pady=5)

    def update_labels(self, _):
        self.thresh_label.configure(text=f"Slouch Sensitivity: {self.thresh_slider.get():.3f}")
        self.delay_label.configure(text=f"Alert Delay: {self.delay_slider.get():.1f}s")

    def play_alert_sound(self):
        """Generates a 0.2 second synthetic beep."""
        fs = 44100  # Standard audio sample rate
        duration = 0.2
        t = np.linspace(0, duration, int(fs * duration), False)
        # 880 Hz is a high, attention-grabbing pitch (A5 note)
        note = 0.5 * np.sin(880 * t * 2 * np.pi) 
        
        # Play asynchronously so it doesn't freeze the video feed
        sd.play(note, fs)

    def update_video_feed(self):
        ret, frame = self.cap.read()

        if ret:
            self.frame_counter += 1
            should_run_ai = (self.frame_counter % 2 == 0)

            frame = self.detector.find_and_draw_pose(frame, run_ai=should_run_ai)

            if should_run_ai:
                self.cached_distance = self.detector.get_posture_data()

            current_time = time.time()

            if self.cached_distance is not None:
                if self.cached_distance > self.thresh_slider.get():
                    
                    if self.bad_posture_start_time is None:
                        self.bad_posture_start_time = current_time
                    
                    elapsed_time = current_time - self.bad_posture_start_time
                    
                    if elapsed_time >= self.delay_slider.get():
                        # --- STATE 3: ALERT BAD POSTURE ---
                        self.status_label.configure(text="Status: ALERT \nBAD POSTURE", text_color="#E74C3C") # Red
                        
                        # Audio Debounce: Only beep once every 1.5 seconds
                        if current_time - self.last_beep_time > 1.5:
                            self.play_alert_sound()
                            self.last_beep_time = current_time
                            
                        # Flashing Logic: Show the warning sign for 0.5s after a beep, then hide it
                        if (current_time - self.last_beep_time) < 0.5:
                            self.warning_label.configure(text="⚠️")
                        else:
                            self.warning_label.configure(text="")
                            
                    else:
                        # --- STATE 2: BAD POSTURE (Grace Period) ---
                        self.status_label.configure(text="Status: Bad Posture...", text_color="#F39C12") # Orange
                        self.warning_label.configure(text="") # Hide warning sign
                        
                else:
                    # --- STATE 1: GOOD POSTURE ---
                    self.bad_posture_start_time = None
                    self.status_label.configure(text="Status: Good", text_color="#2ECC71") # Green
                    self.warning_label.configure(text="") # Hide warning sign

            color_converted = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(color_converted)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(640, 480))
            self.video_label.configure(image=ctk_image)

        self.after(15, self.update_video_feed)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = PostureApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()