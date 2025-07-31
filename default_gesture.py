
def fingers_up(landmarks, hand_type="Right"):
    if not landmarks or len(landmarks) < 21:
        return []

    fingers = []

    # Thumb
    if hand_type == "Right":
        fingers.append(1 if landmarks[4][1] < landmarks[3][1] else 0)
    else:  # Left hand
        fingers.append(1 if landmarks[4][1] > landmarks[3][1] else 0)

    # Fingers
    finger_tips = [8, 12, 16, 20]
    finger_pips = [6, 10, 14, 18]

    for tip, pip in zip(finger_tips, finger_pips):
        fingers.append(1 if landmarks[tip][2] < landmarks[pip][2] else 0)

    return fingers

def detect_gesture(landmarks, hand_type="Right"):
    finger_state = fingers_up(landmarks, hand_type)

    if finger_state == [1, 0, 0, 0, 0]:
        return "prev"
    elif finger_state == [0, 0, 0, 0, 1]:
        return "next"
    elif finger_state == [1, 1, 1, 1, 1]:
        return "zoom_in"
    elif finger_state == [0, 0, 0, 0, 0]:
        return "zoom_out"
    elif finger_state == [0, 1, 0, 0, 0]:
        return "laser_mode_on"
    elif finger_state == [0, 1, 0, 0, 1]:
        return "laser_mode_off"
    elif finger_state == [0, 1, 1, 0, 0]:
        return "toggle_presentation"

    return None
