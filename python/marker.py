import cv2
import numpy as np
class Marker:
    def __init__(self, hsv_low, hsv_high):
        self.hsv_low = np.array(hsv_low)
        self.hsv_high = np.array(hsv_high)
        self.x, self.y = None, None
    def update_position(self, image):
        self.mask = cv2.inRange(image, self.hsv_low, self.hsv_high)
        contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            c = max(contours, key = cv2.contourArea)
            M = cv2.moments(c)
            if M['m00'] != 0:
                self.x = int(M['m10']/M['m00'])
                self.y = int(M['m01']/M['m00'])                
    def pos(self):
        return (self.x, self.y)