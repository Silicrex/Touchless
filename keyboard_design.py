from cv2 import cv2
import numpy  # Button transparency
import cvzone  # Button corners


class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.text = text
        self.size = size


def create_keyboard_keys():
    key_layout = {'top': ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
                  'middle': ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
                  'bottom': ['Z', 'X', 'C', 'V', 'B', 'N', 'M']}

    keys = []
    for i, key in enumerate(key_layout['top']):  # Top row of letters, q-p
        keys.append(Button((100 * i + 50, 150), key))  # Params for position
    for i, key in enumerate(key_layout['middle']):  # a-l
        keys.append(Button((100 * i + 75, 250), key))
    for i, key in enumerate(key_layout['bottom']):  # z-m
        keys.append(Button((100 * i + 100, 350), key))
    keys.append(Button((300, 450), ' ', (300, 85)))  # Spacebar, extra param for different sizing
    keys.append(Button((1100, 150), '<-', (150, 85)))  # Backspace
    keys.append(Button((1100, 250), 'go', (150, 85)))  # Enter
    keys.append(Button((10, 10), '-x', (130, 85)))  # Quit


    return keys


def draw_keyboard(img, keys):  # Takes img, draws keys onto it
    for key in keys:
        x, y = key.pos
        width, height = key.size
        cv2.rectangle(img, key.pos, (x + width, y + height), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, key.text, (x + 16, y + 69), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)
    return img


def draw_transparent_keyboard(img, keys):
    alpha_layer = numpy.zeros_like(img, numpy.uint8)
    for key in keys:
        x, y = key.pos
        width, height = key.size
        rect_color = (255, 0, 255)  # Blue-green-red


        cvzone.cornerRect(alpha_layer, (key.pos[0], key.pos[1], key.size[0], key.size[1]), 20, rt=0)  # Corners
        cv2.rectangle(alpha_layer, key.pos, (x + width, y + height), rect_color, cv2.FILLED)
        cv2.putText(img, key.text, (x + 16, y + 69), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    out = img.copy()
    alpha = 0.3
    mask = alpha_layer.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, alpha_layer, 1 - alpha, 0)[mask]
    return out
