from cv2 import cv2  # For computer vision video capture / display
from cvzone.HandTrackingModule import HandDetector


def hands_only():
    video_capture = cv2.VideoCapture(0)
    video_capture.set(3, 1280)  # Width
    video_capture.set(4, 720)  # Height

    detector = HandDetector(detectionCon=0.8, maxHands=2)  # Params: detector confidence threshold, max hands to detect

    while True:
        success, img = video_capture.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)  # flip off so it acts like a mirror
        hand_count = len(hands)
        # hands = list of hands, hand object is a dict: {lmList, bbox, center, type}

        if hand_count == 1:
            hand1 = hands[0]
            landmarks = hand1['lmList']
            pointer1 = landmarks[8]
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

            distance, _, _ = detector.findDistance(left_pointer, right_pointer, img)
            print(distance)

        cv2.imshow("Image", img)
        cv2.waitKey(1)
