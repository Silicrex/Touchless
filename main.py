from cv2 import cv2  # For computer vision video capture / display
from cvzone.HandTrackingModule import HandDetector
import time  # To debounce keys
from pynput.keyboard import Key, Controller  # Simulating keyboard input
import win32gui  # win32gui and win32con for pinning window
import win32con
import keyboard_design
from playsound import playsound
import modes


# Video capture, hand detector, keyboard design
video_capture = cv2.VideoCapture(0)
video_capture.set(3, 1280)  # Width
video_capture.set(4, 720)  # Height

detector = HandDetector(detectionCon=0.8, maxHands=2)  # Params: detector confidence threshold, max hands to detect
keyboard = Controller()
keyboard_uppercase = keyboard_design.create_keyboard_keys()
keyboard_lowercase = keyboard_design.create_keyboard_keys(caps=False)


def main():
    key_cooldown = 0.15  # Cooldown for key presses in seconds

    key_monotonic = 0
    color_monotonic = 0
    key_pressed = None
    pinned = False
    opacity = True
    caps = True
    live_text = []
    while True:
        success, img = video_capture.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)  # flip off so it acts like a mirror
        hand_count = len(hands)
        # hands = list of hands, hand object is a dict: {lmList, bbox, center, type}

        if caps:
            keyboard_layout = keyboard_uppercase
        else:
            keyboard_layout = keyboard_lowercase

        if opacity:
            img = keyboard_design.draw_transparent_keyboard(img, keyboard_layout)  # Draw keyboard
        else:
            img = keyboard_design.draw_keyboard(img, keyboard_layout)

        if hand_count == 1:
            hand1 = hands[0]
            landmarks = hand1['lmList']
            pointer1 = landmarks[8]

            for key in keyboard_layout:
                x, y = key.pos
                width, height = key.size
                if x < pointer1[0] < x + width and y < pointer1[1] < y + height:
                    cv2.rectangle(img, key.pos, (x + width, y + height), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, key.text, (x + 16, y + 69), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
        elif hand_count == 2:
            right_hand = hands[0] if hands[0]['type'] == 'Right' else hands[1]
            right_landmarks = right_hand['lmList']

            left_hand = hands[0] if hands[0]['type'] == 'Left' else hands[1]
            left_landmarks = left_hand['lmList']

            # For landmarks: 4-8-12-16-20 thumb to pinky tip. Each has 4 points total, 3 going down from the tip
            # landmark 0 is where your palm meets your wrist
            # Value at landmark index is x/y coordinates
            # ----- Preset landmark bindings (x/y coordinates)
            right_thumb = right_landmarks[4]
            right_pointer = right_landmarks[8]
            right_middle = right_landmarks[12]
            right_ring = right_landmarks[16]
            right_pinky = right_landmarks[20]

            left_thumb = left_landmarks[4]
            left_pointer = left_landmarks[8]
            left_middle = left_landmarks[12]
            left_ring = left_landmarks[16]
            left_pinky = left_landmarks[20]
            # -----

            distance, _, _ = detector.findDistance(right_thumb, right_pinky, img)
            print(distance)

            for key in keyboard_layout:
                x, y = key.pos
                width, height = key.size
                if x < left_pointer[0] < x + width and y < left_pointer[1] < y + height:
                    if time.monotonic() > color_monotonic or key_pressed != key.text:
                        cv2.rectangle(img, key.pos, (x + width, y + height), (0, 255, 0), cv2.FILLED)
                        color_monotonic = 0
                    else:
                        cv2.rectangle(img, (key.pos[0] - 10, key.pos[1] - 10), (x + width + 10, y + height + 10),
                                      (0, 0, 255), cv2.FILLED)
                    cv2.putText(img, key.text, (x + 16, y + 69), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
                    if hand_count == 2:
                        if distance < 105:
                            if time.monotonic() > key_monotonic:
                                playsound('press.mp3', False)
                                key_monotonic = time.monotonic() + key_cooldown
                                if key.text == '<-':
                                    keyboard.press(Key.backspace)
                                    if live_text:
                                        live_text.pop()
                                elif key.text == 'go':
                                    keyboard.press(Key.enter)
                                    live_text.clear()
                                elif key.text == 'op':
                                    opacity = not opacity  # Toggle
                                elif key.text == '^^':
                                    caps = not caps  # Toggle
                                elif key.text == '-x':
                                    quit()
                                else:
                                    keyboard.press(key.text)
                                    key_pressed = key.text
                                    live_text.append(key.text)
                                    if len(live_text) > 24:
                                        live_text.pop(0)
                                color_monotonic = time.monotonic() + 0.15
        cv2.rectangle(img, (50, 600), (1230, 750), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, ''.join(live_text), (60, 675), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

        cv2.imshow("Touchless", img)
        if not pinned:
            hwnd = win32gui.FindWindow(None, "Touchless")
            print(hwnd)
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 600, 50, 1280, 720, 0)
            pinned = True
        cv2.waitKey(1)


main()
