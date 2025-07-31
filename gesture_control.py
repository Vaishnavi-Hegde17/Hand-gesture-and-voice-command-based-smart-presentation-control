import json
import os

GESTURE_FILE = "gesture_database.json"

def fingers_up(landmarks, hand_type="Right"):
    if not landmarks or len(landmarks) < 21:
        return []

    fingers = []

    # Thumb
    if hand_type == "Right":
        fingers.append(1 if landmarks[4][1] < landmarks[3][1] else 0)
    else:
        fingers.append(1 if landmarks[4][1] > landmarks[3][1] else 0)

    # Fingers: Tip above PIP means finger is up
    tip_ids = [8, 12, 16, 20]
    pip_ids = [6, 10, 14, 18]

    for tip, pip in zip(tip_ids, pip_ids):
        fingers.append(1 if landmarks[tip][2] < landmarks[pip][2] else 0)

    return fingers

def save_new_gesture(action, landmarks, hand_type="Right"):
    gesture_key = str(fingers_up(landmarks, hand_type))

    if os.path.exists(GESTURE_FILE):
        with open(GESTURE_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[gesture_key] = action

    with open(GESTURE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved: {gesture_key} ➝ {action}")

def match_gesture(landmarks, hand_type="Right"):
    finger_state = str(fingers_up(landmarks, hand_type))

    if not os.path.exists(GESTURE_FILE):
        return None

    with open(GESTURE_FILE, "r") as f:
        data = json.load(f)

    action = data.get(finger_state)
    if action:
        print(f"Matched {finger_state} ➝ {action}")
    return action
