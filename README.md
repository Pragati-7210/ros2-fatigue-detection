#ROS2 Multimodal Fatigue Detection System

## Overview

This project is a ROS2-based multimodal fatigue detection system that combines:

* Eye fatigue detection
* Yawn detection
* Head posture monitoring
* Typing activity monitoring
* Privacy-aware permissions system
* Sensor fusion
* Alert generation
* Dataset logging

The system uses:

* ROS2 Jazzy
* Python
* OpenCV
* MediaPipe FaceMesh

---

# Current Architecture

## ROS2 Packages

| Package        | Purpose                             |
| -------------- | ----------------------------------- |
| `camera_pkg`   | Webcam + MediaPipe processing       |
| `fusion_pkg`   | Multimodal fatigue score generation |
| `settings_pkg` | Privacy and permission management   |
| `alert_pkg`    | Fatigue alert generation            |
| `typing_pkg`   | Keyboard activity monitoring        |
| `launch_pkg`   | Launches entire ROS2 system         |

---

# Features Implemented

## Camera Pipeline

Implemented:

* Real-time webcam capture
* MediaPipe FaceMesh integration
* Eye Aspect Ratio (EAR) calculation
* Mouth Aspect Ratio (MAR) calculation
* Head posture estimation
* Live overlays
* ROS2 topic publishing

### Published Topics

| Topic           | Type      | Description         |
| --------------- | --------- | ------------------- |
| `/eye_data`     | `Float32` | Eye fatigue metric  |
| `/yawn_data`    | `Float32` | Yawn metric         |
| `/posture_data` | `Float32` | Head posture metric |

---

## Fusion Pipeline

The fusion node:

* Subscribes to all sensor topics
* Applies privacy permissions
* Computes fatigue score
* Publishes fused fatigue output
* Logs synchronized multimodal dataset

### Fusion Topics

| Topic            | Type      | Description           |
| ---------------- | --------- | --------------------- |
| `/fatigue_score` | `Float32` | Final fatigue score   |
| `/permissions`   | `String`  | Privacy settings JSON |

---

## Privacy / Permissions System

Implemented:

* Camera permission control
* Typing permission control
* Privacy modes

Current modes:

* FULL_MONITORING
* PRIVACY_MODE
* MINIMAL_MODE

---

## Alert System

The alert node:

* Subscribes to fatigue score
* Detects fatigue thresholds
* Generates fatigue alerts

Current fatigue levels:

* NORMAL
* MODERATE FATIGUE
* SEVERE FATIGUE

---

## Dataset Logging

The fusion node automatically generates:

```text
~/fatigue_dataset.csv
```

### Current CSV Format

```text
timestamp,eye,yawn,posture,typing,fatigue_score
```

### Logging Frequency

Current logging rate:

* ~1 sample/sec

---

# Installation

## System Requirements

* Ubuntu 24.04
* ROS2 Jazzy
* Python 3.12

---

# Dependencies

Install Python dependencies:

```bash
python3 -m pip install mediapipe==0.10.13 --break-system-packages
python3 -m pip install "numpy<2.0" --break-system-packages
python3 -m pip install opencv-python --break-system-packages
```

---

# Build Instructions

## Clone Repository

```bash
git clone https://github.com/Pragati-7210/ros2-fatigue-detection.git
```

## Navigate to Workspace

```bash
cd ros2-fatigue-detection
```

## Build Workspace

```bash
colcon build
```

## Source Workspace

```bash
source install/setup.bash
```

---

# Running the System

## Launch Entire System

```bash
ros2 launch launch_pkg system_launch.py
```

---

# ROS2 Topic Testing

## View Eye Data

```bash
ros2 topic echo /eye_data
```

## View Fatigue Score

```bash
ros2 topic echo /fatigue_score
```

## View Permissions

```bash
ros2 topic echo /permissions
```

---

# Current Limitations

## Typing Node

Typing modality still needs:

* stabilization
* calibration
* better activity normalization

---

## Fusion Logic

Current fatigue scoring uses:

* handcrafted heuristic logic

Future improvements:

* smoothing
* normalization
* ML-based inference

---

## Dataset Quality

Current dataset still lacks:

* fatigue labels
* session annotations
* ground truth validation

---

# Planned Future Work

## ML Integration

Planned:

* feature engineering
* fatigue classification models
* temporal modeling
* inference deployment into ROS2

Possible models:

* Random Forest
* XGBoost
* LSTM

---

## System Improvements

Planned improvements:

* signal smoothing
* better posture metrics
* typing activity normalization
* dashboard/UI
* live analytics
* model inference node

---

# Team Responsibilities

| Team Member | Responsibility                     |
| ----------- | ---------------------------------- |
| Pragathi    | ROS2 integration + sensor pipeline |
| Rushikesh   | ML model development               |
| Akansha     | Privacy/settings workflows         |
| Gaurav      | Dashboard/UI/visualization         |

---

# Important Notes

## Do NOT Commit

These folders/files should never be pushed:

```text
build/
install/
log/
venv/
__pycache__/
*.csv
```

---

# Repository

GitHub Repository:

[https://github.com/Pragati-7210/ros2-fatigue-detection](https://github.com/Pragati-7210/ros2-fatigue-detection)
