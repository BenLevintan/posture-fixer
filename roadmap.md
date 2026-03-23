# Posture Detection App — Game Plan

## Overview
Android app that uses the front camera + ML Kit Pose Detection to detect bad posture and play a warning sound.

---

## Tech Stack
- **Camera:** CameraX (lifecycle-aware, easy analysis stream)
- **Pose Detection:** ML Kit Pose Detection (on-device, real-time, 33 landmarks)
- **Audio:** SoundPool (low-latency beep)
- **UI:** Jetpack Compose

---

## Architecture
```
CameraX (front camera)
    │
    ▼
ImageAnalysis (frame-by-frame)
    │
    ▼
ML Kit Pose Detector
    │  (33 body landmarks: x, y, confidence)
    ▼
PostureAnalyzer
    │  - shoulder tilt: |leftShoulder.y - rightShoulder.y| > threshold
    │  - head drop:     nose.y > shoulderMidY + threshold
    │  - confidence:    skip frame if landmark confidence < 0.6
    ▼
PostureState: GOOD | BAD | UNKNOWN
    │
    ▼
AlertManager
    ├── debounce: only alert after 3s of continuous bad posture
    ├── cooldown: alert at most once every 10s
    ├── SoundPool → beep
    └── Vibrator → haptic pulse
```

---

## File Structure
```
app/src/main/java/com/yourapp/posture/
├── camera/
│   ├── CameraManager.kt       # CameraX setup
│   └── PoseAnalyzer.kt        # ImageAnalysis + ML Kit
├── posture/
│   ├── PostureAnalyzer.kt     # Landmark math → PostureState
│   └── PostureState.kt        # enum: GOOD, BAD, UNKNOWN
├── alert/
│   └── AlertManager.kt        # Sound + vibration + debounce
└── ui/
    └── CameraScreen.kt        # Compose preview + status indicator
```

---

## Key Landmarks to Watch

| Check | Landmarks | Condition |
|---|---|---|
| Shoulder tilt | LEFT_SHOULDER, RIGHT_SHOULDER | `|y_left - y_right| > 40px` |
| Head drop / slouch | NOSE, shoulder midpoint | `nose.y > midY + 60px` |
| Forward neck | LEFT_EAR, LEFT_SHOULDER | `ear.y > shoulder.y + 50px` |

> Thresholds are in image pixels — calibrate on a real device.

---

## Gotchas
- **Front camera is mirrored** — left/right landmarks are flipped in image space
- **Normalize coordinates** by image width/height for device-independent thresholds
- **Throttle analysis** to every 2–3 frames to save battery (ML Kit STREAM_MODE is CPU-heavy)
- **Handle UNKNOWN gracefully** — low confidence = bad lighting or wrong device angle, don't alert