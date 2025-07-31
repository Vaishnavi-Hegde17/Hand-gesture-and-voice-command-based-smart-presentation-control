import speech_recognition as sr
from presentation_control import control_presentation

def recognize_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print(" Listening for voice commands...")

        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"Voice Command: {command}")
            return command
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError:
            print(" Could not connect to speech service")
            return None

import re
from word2number import w2n

def handle_voice_command(command):
    if command is None:
        return

    command = command.lower()
    print(f"Received command: '{command}'")

    if "start presentation" in command:
        control_presentation("toggle_presentation")
    elif "stop presentation" in command:
        control_presentation("toggle_presentation")
    elif "next slide" in command or "next" in command:
        control_presentation("next")
    elif "previous slide" in command or "previous" in command:
        control_presentation("prev")
    elif "laser pointer on" in command or "enable laser" in command:
        control_presentation("laser_mode_on")
    elif "laser pointer off" in command or "disable laser" in command:
        control_presentation("laser_mode_off")

    # Case 1: Command contains phrase like "slide 3"
    elif re.search(r"(go to slide|slide number|slide)\s+(\d+)", command):
        match = re.search(r"(go to slide|slide number|slide)\s+(\d+)", command)
        if match:
            slide_number = int(match.group(2))
            control_presentation("goto_slide", slide_number)
        else:
            print("Could not extract slide number from command.")

    # Case 2: Just a number (e.g., "3") or word (e.g., "three")
    elif re.fullmatch(r"\d+", command.strip()):
        slide_number = int(command.strip())
        control_presentation("goto_slide", slide_number)

    elif re.fullmatch(r"[a-z\s\-]+", command.strip()):
        try:
            slide_number = w2n.word_to_num(command.strip())
            control_presentation("goto_slide", slide_number)
        except ValueError:
            print("Could not convert spoken word to number.")
    else:
        print("Unrecognized command")
