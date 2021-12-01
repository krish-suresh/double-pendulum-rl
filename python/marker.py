import cv2
import numpy as np
class Marker:
    def __init__(self, hsv_low, hsv_high, second_low=None, second_high=None):
        self.hsv_low = np.array(hsv_low)
        self.hsv_high = np.array(hsv_high)
        self.hsv_second_low = np.array(second_low) if second_low else None
        self.hsv_second_high = np.array(second_high) if second_high else None
        self.x, self.y, self.c = None, None, None
    def update_position(self, image):
        # self.img = image
        self.mask = cv2.inRange(image, self.hsv_low, self.hsv_high)
        if self.hsv_second_low is not None:
            second_mask = cv2.inRange(image, self.hsv_second_low, self.hsv_second_high)
            self.mask = cv2.bitwise_or(self.mask, second_mask)
        contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            self.c = max(contours, key = cv2.contourArea)
            M = cv2.moments(self.c)
            if M['m00'] != 0:
                self.x = int(M['m10']/M['m00'])
                self.y = int(M['m01']/M['m00'])                
    def pos(self):
        return (self.x, self.y)