import tkinter as tk
from tkinter import messagebox
import threading
import time
import os
import json
import cv2
import numpy as np
import mediapipe as mp

from gesture_control import match_gesture, save_new_gesture, fingers_up
from HandTracker import HandTracker
from presentation_control import (
    control_presentation,
    move_laser_pointer,
    zoom_at_position,
    is_zoomed_in
)
from utils import is_valid_hand_distance, calculate_distance
from voice_command import recognize_command, handle_voice_command

GESTURE_FILE = "gesture_database.json"
stop_flag = False


def load_or_init_gesture_data():
    default = {
        "[0, 1, 1, 0, 0]": "toggle_presentation",
        "[1, 0, 0, 0, 0]": "prev",
        "[0, 0, 0, 0, 1]": "next",
        "[1, 1, 1, 1, 1]": "zoom_in",
        "[0, 0, 0, 0, 0]": "zoom_out",
        "[0, 1, 0, 0, 0]": "laser_mode_on",
        "[0, 1, 0, 0, 1]": "laser_mode_off"
    }

    if not os.path.exists(GESTURE_FILE):
        with open(GESTURE_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default

    with open(GESTURE_FILE, "r") as f:
        data = json.load(f)

    return data


def ui_popup():
    gesture_action_map = load_or_init_gesture_data()

    def on_continue():
        root.destroy()
        start_system()

    def on_customize():
        root.destroy()
        record_custom_gestures()
        start_system()

    root = tk.Tk()
    root.title("Smart Presentation Tool Setup")
    root.geometry("550x420")

    label = tk.Label(root, text="\nSmart Presentation Gesture Controls\n", font=("Arial", 16))
    label.pack()

    gesture_text = ""
    for pattern, action in gesture_action_map.items():
        try:
            state = json.loads(pattern)
            label_map = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
            raised = [label_map[i] for i, val in enumerate(state) if val == 1]
            raised_str = ", ".join(raised) if raised else "None"
            gesture_text += f"[{','.join(map(str, state))}] ({raised_str}) → {action}\n"
        except:
            gesture_text += f"{pattern} → {action}\n"

    text = tk.Text(root, height=12, wrap=tk.WORD)
    text.insert(tk.END, gesture_text)
    text.config(state=tk.DISABLED)
    text.pack(pady=10)

    label2 = tk.Label(root, text="Do you want to continue with these gestures or customize them?", font=("Arial", 12))
    label2.pack()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    continue_btn = tk.Button(button_frame, text="Continue", command=on_continue, width=15, bg="lightgreen")
    continue_btn.grid(row=0, column=0, padx=10)

    customize_btn = tk.Button(button_frame, text="Customize", command=on_customize, width=15, bg="orange")
    customize_btn.grid(row=0, column=1, padx=10)

    root.mainloop()


def record_custom_gestures():
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)

    actions = [
        "toggle_presentation",
        "next",
        "prev",
        "zoom_in",
        "zoom_out",
        "laser_mode_on",
        "laser_mode_off"
    ]

    gesture_data = {}

    for action in actions:
        print(f"Show gesture for: {action}")
        print("   Press 's' to save it OR 'q' to skip.")

        while True:
            ret, frame = cap.read()
            frame, landmarks, _, hand_type = tracker.find_hands(frame)

            if landmarks:
                for _, x, y in landmarks:
                    cv2.circle(frame, (x, y), 5, (255, 0, 0), -1)

            cv2.putText(frame, f"Gesture: {action}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
            cv2.putText(frame, "Press 's' to SAVE | 'q' to SKIP", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 200), 2)
            cv2.imshow("Record Gesture", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s') and landmarks:
                finger_state = fingers_up(landmarks, hand_type)
                gesture_data[str(finger_state)] = action
                print(f" Saved gesture for '{action}' as {finger_state}")
                break
            elif key == ord('q'):
                print(f"Skipped gesture for '{action}'")
                break

    cap.release()
    cv2.destroyAllWindows()

    with open(GESTURE_FILE, "w") as f:
        json.dump(gesture_data, f, indent=2)
    print("All custom gestures saved.")


def voice_loop():
    global stop_flag
    while not stop_flag:
        command = recognize_command()
        handle_voice_command(command)


def start_system():
    global stop_flag
    mp_seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)

    gesture_action_map = load_or_init_gesture_data()

    voice_thread = threading.Thread(target=voice_loop, daemon=True)
    voice_thread.start()

    current_gesture = None
    gesture_start_time = None
    gesture_confirmed = None
    hold_duration = 2

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = mp_seg.process(rgb)
        mask = result.segmentation_mask > 0.5
        blurred_bg = cv2.GaussianBlur(frame, (55, 55), 0)
        frame = np.where(mask[..., None], frame, blurred_bg)

        frame, landmarks, _, hand_type = tracker.find_hands(frame)

        if landmarks:
            dist = calculate_distance(landmarks[0], landmarks[4])

            # Show distance guidance
            cv2.putText(frame, "Hand distance range: 15–50 cm from camera", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, f"Current distance: {int(dist)} px", (10, 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            if dist < 10:
                cv2.putText(frame, "Move hand slightly farther", (10, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            elif dist > 300:
                cv2.putText(frame, "Move hand closer to camera", (10, 85),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        if landmarks and is_valid_hand_distance(landmarks):
            finger_state = fingers_up(landmarks, hand_type)
            gesture_key = str(finger_state)
            action = gesture_action_map.get(gesture_key)

            if gesture_key == current_gesture and action:
                elapsed = time.time() - gesture_start_time
                if elapsed >= hold_duration and gesture_confirmed != gesture_key:
                    gesture_confirmed = gesture_key
                    print(f"Confirmed Action: {action}")
                    control_presentation(action)

                    if action in ["zoom_in", "zoom_out"] and len(landmarks) > 8:
                        ix, iy = landmarks[8][1], landmarks[8][2]
                        h, w = frame.shape[:2]
                        if action == "zoom_out" and not is_zoomed_in():
                            print("Skipping zoom out — not currently zoomed in.")
                        else:
                            zoom_at_position(ix, iy, w, h, zoom_in=(action == "zoom_in"))

                elif elapsed < hold_duration:
                    cv2.putText(frame, f"Holding: {action} ({elapsed:.1f}s)", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            elif gesture_key != current_gesture:
                current_gesture = gesture_key
                gesture_start_time = time.time()
                gesture_confirmed = None

            if action:
                cv2.putText(frame, f"Detected: {action}", (10, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            if action == "laser_mode_on" and len(landmarks) > 8:
                ix, iy = landmarks[8][1], landmarks[8][2]
                h, w = frame.shape[:2]
                move_laser_pointer(ix, iy, w, h)
        else:
            current_gesture = None
            gesture_start_time = None
            gesture_confirmed = None
            cv2.putText(frame, "Show gesture in frame", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.putText(frame, "Press 'c' to Close", (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

        cv2.imshow("Smart Presentation Controller", frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):
            stop_flag = True
            time.sleep(1)
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    ui_popup()
