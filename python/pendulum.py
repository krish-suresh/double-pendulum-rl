import subprocess
from marker import Marker
import numpy as np
import cv2
import math
import time
def jrk2cmd(*args):
  return subprocess.check_output(['jrk2cmd'] + list(args))
def angle_wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi
class Pendulum:
    def __init__(self):
        self.slide_marker = Marker([170, 130, 70],[180, 255, 255], second_low=[0, 180, 130], second_high=[5, 255, 255])
        self.joint_0_marker = Marker([40, 30, 100],[70, 255, 255])
        self.joint_1_marker = Marker([90, 150,130],[130, 255,255])
        self.left_end_marker = Marker([150, 70, 130],[170, 255, 255])
        self.right_end_marker = Marker([150, 70, 130],[170, 255, 255])
        self.ENDSTOP_THRESH = 0.2
        self.first_step = True
        self.action_space = np.array([-1, 1])
        self.state_space = np.array([])
        self.current_action = 0

    def update_state(self, image):
        # update marker positions
        self.slide_marker.update_position(image)
        self.joint_0_marker.update_position(image)
        self.joint_1_marker.update_position(image)
        left_blocked = cv2.rectangle(image.copy(), (0,0), (int(image.shape[1]/2), image.shape[0]), (0,0,0), -1)
        right_blocked = cv2.rectangle(image.copy(), (int(image.shape[1]/2), 0), (image.shape[1], image.shape[0]), (0,0,0), -1)
        self.right_end_marker.update_position(left_blocked)
        self.left_end_marker.update_position(right_blocked)
        img_wait = False
        for marker in [self.slide_marker, self.joint_0_marker,self.joint_1_marker, self.right_end_marker, self.left_end_marker]:
            if marker.x is None:
                img_wait = True
        # calculate pendulum state
        if not img_wait:
            if self.first_step:
                self.first_step = False
                self.update_positions()
                self.slide_pos_dot, self.arm_0_theta_dot, self.arm_1_theta_dot = 0, 0, 0 # on first step all velocities are 0
            else:
                slide_pos_prev, arm_0_theta_prev, arm_1_theta_prev = self.slide_pos, self.arm_0_theta, self. arm_1_theta # store prev positions
                self.update_positions()
                time_diff = time.perf_counter() - self.time_prev
                self.slide_pos_dot = (self.slide_pos - slide_pos_prev) / time_diff
                self.arm_0_theta_dot = (self.arm_0_theta - arm_0_theta_prev) / time_diff
                self.arm_1_theta_dot = (self.arm_1_theta - arm_1_theta_prev) / time_diff  
                if self.current_action != 0 and (self.is_near_left_end_stop() or self.is_near_left_end_stop()):
                    self.set_motor(0)
        self.time_prev = time.perf_counter()
            
    def update_positions(self):
        self.slide_pos = np.linalg.norm(self.slide_marker.x - self.left_end_marker.x)/np.linalg.norm(self.right_end_marker.x - self.left_end_marker.x)-0.5
        self.arm_0_theta = angle_wrap(math.atan2(self.joint_0_marker.y-self.slide_marker.y, self.joint_0_marker.x-self.slide_marker.x) + np.pi/2)
        self.arm_1_theta = angle_wrap(math.atan2(self.joint_1_marker.y-self.joint_0_marker.y, self.joint_1_marker.x-self.joint_0_marker.x) + np.pi/2)

    def state(self):
        return (self.slide_pos, self.arm_0_theta, self.arm_1_theta, self.slide_pos_dot, self.arm_0_theta_dot, self.arm_1_theta_dot) if not self.first_step else None
    def reward(self):
        pos_reward = 0.5 - abs(self.slide_pos)*10
        arm_0_reward = np.pi - abs(self.arm_0_theta)*10
        arm_1_reward = np.pi - abs(self.arm_1_theta)*10
        pos_dot_reward = 1 - abs(self.slide_pos_dot)/2
        arm_0_dot_reward = 6 - abs(self.arm_0_theta_dot)
        arm_1_dot_reward = 6 - abs(self.arm_1_theta_dot)
        return pos_reward + arm_0_reward + arm_1_reward + pos_dot_reward + arm_0_dot_reward + arm_1_dot_reward

    def formatted_state(self):
        if self.state():
            return f"""x = {self.slide_pos}
theta_0 = {self.arm_0_theta}
theta_1 = {self.arm_1_theta}
x_dot = {self.slide_pos_dot}
theta_0_dot = {self.arm_0_theta_dot}
theta_1_dot = {self.arm_0_theta_dot}
is_at_edge = L: {self.is_near_left_end_stop()} R: {self.is_near_right_end_stop()}
current_power= {self.current_action}
"""
        else:
            return None
    def is_near_left_end_stop(self):
        return  0.5 + self.slide_pos < self.ENDSTOP_THRESH
    def is_near_right_end_stop(self):
        return 0.5 - self.slide_pos < self.ENDSTOP_THRESH
    def set_motor(self, target_power, limits=True):
        '''target_power: value between -1 and 1'''
        target_power = np.clip(target_power, -1, 1)
        if limits and not self.first_step and self.is_near_left_end_stop():
            target_power = np.clip(target_power, 0, 1)
        elif limits and not self.first_step and self.is_near_right_end_stop():
            target_power = np.clip(target_power, -1, 0)
        self.current_action = target_power
        target_converted = int((target_power+1)*2048)
        jrk2cmd('--target', str(target_converted))