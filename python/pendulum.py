import subprocess
from marker import Marker
import numpy as np
import cv2
import math

def jrk2cmd(*args):
  return subprocess.check_output(['jrk2cmd'] + list(args))
def angle_wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi
class Pendulum:
    def __init__(self):
        self.slide_marker = Marker([0,50,50],[50, 255, 255])
        self.joint_0_marker = Marker([0,50,50],[50, 255, 255])
        self.joint_1_marker = Marker([0,50,50],[50, 255, 255])
        self.left_end_marker = Marker([0,50,50],[50, 255, 255])
        self.right_end_marker = Marker([0,50,50],[50, 255, 255])
        self.ENDSTOP_THRESH = 0.1
    def update_state(self, image):
        # update marker positions
        self.slide_marker.update_position(image)
        self.joint_0_marker.update_position(image)
        self.joint_1_marker.update_position(image)
        left_blocked = cv2.rectangle(image, (0,0), (image.shape[0]/2, image.shape[1]), (0,0,0), -1)
        right_blocked = cv2.rectangle(image, (image.shape[0]/2, 0), (image.shape[0], image.shape[1]), (0,0,0), -1)
        self.right_end_marker.update_position(left_blocked)
        self.left_end_marker.update_position(right_blocked)
        # calculate pendulum state
        self.slide_pos = np.linalg.norm(self.slide_marker.x - self.left_end_marker.x)/np.linalg.norm(self.right_end_marker.x - self.left_end_marker.x)-0.5
        self.arm_0_theta = angle_wrap(math.atan2(self.arm_0_theta.y-self.slide_marker.y, self.arm_0_theta.x-self.slide_marker.x) + np.pi/2)
        self.arm_1_theta = angle_wrap(math.atan2(self.arm_1_theta.y-self.arm_0_theta.y, self.arm_1_theta.x-self.arm_0_theta.x) + np.pi/2)
    def state(self):
        return (self.slide_pos, self.arm_0_theta, self. arm_1_theta)
    def is_near_left_end_stop(self):
        return  0.5 + self.slide_pos < self.ENDSTOP_THRESH
    def is_near_right_end_stop(self):
        return 0.5 - self.slide_pos < self.ENDSTOP_THRESH
    def set_motor(self, target_power):
        '''target_power: value between -1 and 1'''
        target_power = np.clip(target_power, -1, 1)
        if self.is_near_left_end_stop():
            target_power = np.clip(target_power, 0, 1)
        elif self.is_near_right_end_stop:
            target_power = np.clip(target_power, -1, 0)
        target_converted = (target_power+1)*2048
        jrk2cmd('--target', str(target_converted))