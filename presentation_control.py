import pyautogui
import pygetwindow as gw
import time

# Global state flags
presentation_mode = False
laser_mode = False
zoom_level = 0  # Replaces boolean zoom_mode

def focus_powerpoint_window():
    windows = gw.getWindowsWithTitle('PowerPoint')
    if windows:
        ppt_window = windows[0]
        ppt_window.activate()
        time.sleep(0.5)
        return True
    else:
        print(" PowerPoint window not found.")
        return False

def control_presentation(action,value=None):
    global presentation_mode, laser_mode

    if action == "toggle_presentation":
        if focus_powerpoint_window():
            if not presentation_mode:
                pyautogui.press("f5")
                presentation_mode = True
                print(" Presentation Started")
            else:
                pyautogui.press("esc")
                presentation_mode = False
                print(" Presentation Stopped")

    elif action == "next":
        pyautogui.press("right")
        print(" Slide: Next")

    elif action == "prev":
        pyautogui.press("left")
        print(" Slide: Previous")

    elif action == "zoom_in":
        print("Gesture confirmed: zoom_in")
        pass

    elif action == "zoom_out":
        print("Gesture confirmed: zoom_out")
        pass

    elif action == "laser_mode_on":
        pyautogui.hotkey("ctrl", "l")
        laser_mode = True
        print("Laser Pointer ON")

    elif action == "laser_mode_off":
        pyautogui.hotkey("ctrl", "l")
        laser_mode = False
        print(" Laser Pointer OFF")

    elif action == "goto_slide" and isinstance(value, int):
        # Use 'ctrl + s' to open slide number box in PowerPoint
        pyautogui.hotkey('ctrl', 's')
        pyautogui.typewrite(str(value))
        pyautogui.press('enter')

def is_zoomed_in():
    return zoom_level > 0

def move_laser_pointer(cam_x, cam_y, cam_width, cam_height):
    screen_w, screen_h = pyautogui.size()
    # Flip x to fix mirrored movement
    screen_x = screen_w - int(cam_x / cam_width * screen_w)
    screen_y = int(cam_y / cam_height * screen_h)
    pyautogui.moveTo(screen_x, screen_y)

def zoom_at_position(cam_x, cam_y, cam_width, cam_height, zoom_in=True):
    global zoom_level
    screen_w, screen_h = pyautogui.size()
    screen_x = int(cam_x / cam_width * screen_w)
    screen_y = int(cam_y / cam_height * screen_h)

    pyautogui.moveTo(screen_x, screen_y)
    pyautogui.keyDown('ctrl')
    pyautogui.scroll(100 if zoom_in else -100)
    pyautogui.keyUp('ctrl')

    if zoom_in:
        zoom_level += 1
        print(f" Zoomed In at ({screen_x}, {screen_y}) | Level: {zoom_level}")
    else:
        if zoom_level > 0:
            zoom_level -= 1
            print(f" Zoomed Out at ({screen_x}, {screen_y}) | Level: {zoom_level}")
        else:
            print(" Skipping zoom out — already fully zoomed out.")
