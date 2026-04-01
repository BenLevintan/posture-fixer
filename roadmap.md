# Posture Detection App — Game Plan

## Overview
Android app that uses the front camera + ML Kit Pose Detection to detect bad posture and play a warning sound. Features a 3-state warning system (Good, Warning, Alert), adjustable sensitivity, and a privacy/battery-saving mode that hides the camera feed while maintaining background analysis.

---

## Tech Stack
- **Camera:** CameraX (lifecycle-aware, easy analysis stream)
- **Pose Detection:** ML Kit Pose Detection (`FAST` mode for battery optimization, 33 landmarks)
- **Audio:** SoundPool (low-latency synthetic beep)
- **UI:** Jetpack Compose (Modern, reactive UI with Dark Mode support)
- **Storage:** DataStore / SharedPreferences (for saving user sensitivity/delay configs)

---

## Architecture
```text
CameraX (front camera)
    │
    ▼
ImageAnalysis (frame-by-frame, throttled to save CPU)
    │
    ▼
ML Kit Pose Detector (FAST Model)
    │  (33 body landmarks: x, y, confidence)
    ▼
PostureAnalyzer
    │  - Extract: Left/Right Shoulder, Left/Right Mouth
    │  - Math: Calculate perpendicular distance from Mouth corners to the infinite line drawn between Shoulders.
    │  - Confidence: Skip frame if landmark confidence < 0.6
    ▼
PostureState: GOOD | WARNING (Grace Period) | ALERT | UNKNOWN
    │
    ▼
AlertManager
    ├── timer: tracks continuous time in WARNING state
    ├── triggers ALERT if time > UserConfig.Delay
    ├── cooldown: alert at most once every X seconds
    └── SoundPool → beep
