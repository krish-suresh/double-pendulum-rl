import serial
import time
import subprocess
import numpy as np
import math
import time
import gym
from gym import spaces
from gym.utils import seeding
import re
def jrk2cmd(*args):
  return subprocess.check_output(['jrk2cmd'] + list(args))
def angle_wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


class Pendulum(gym.Env):
    def __init__(self):
        # self.arduino = serial.Serial('/dev/ttyACM3', 115200)
        self.arduino = serial.Serial()
        self.arduino.port = "/dev/ttyACM0"
        self.arduino.baudrate = 115200
        self.arduino.timeout = 1
        self.arduino.setDTR(False)
        #arduinoSerialData.setRTS(False)
        self.arduino.open()
        self.ENDSTOP_DIST = 120/1000 # mm
        self.state = np.zeros(3)
        high = np.array([self.ENDSTOP_DIST, math.pi, math.pi, 20, 20, 20], dtype=np.float32)
        self.action_space = spaces.Box(
            low=-1, high=1, shape=(1,), dtype=np.float32
        )
        self.observation_space = spaces.Box(low=-high, high=high, dtype=np.float32)
        self.current_action = 0
        self.arm_0_length = 140/1000 # m
        self.arm_1_length = 120/1000 # mm
        self.reward = 0
        self.dist_penalty = 0
        self.vel_penalty = 0

        for i in range(50):
            self.update_state()
    def update_state(self):
        try:
            line = self.arduino.readline()
            # re.sub('[^0-9].','', x)
            a = np.array([float(x) for x in line.decode("utf-8", "replace").strip().split(',')])  
            if len(a) == 3:
                self.state = a
                self.state[1] = np.cos(self.state[1], dtype=np.float32)
        except:
            print('failed read')
            print(line)
    def step(self, action, check_pos = False):
        # update marker positions
        self.set_motor(action)
        self.update_state()
        self.reward = self.state[1]
        done = self.is_near_left_end_stop() or self.is_near_right_end_stop()
        return self.state, self.reward, done, {}
        # return np.zeros(6), 0, False, {}
    def reset(self):
        self.set_motor(0)
        input("[ENTER] when reset")
        for i in range(100):
            self.update_state()
        return self.state
    def tip_pos(self):
        x = self.state[0]
        y = -self.arm_0_length-self.arm_1_length

        x+= math.sin(self.state[1]) * self.arm_0_length
        y+= math.cos(self.state[1]) * self.arm_0_length

        return x,y
    def formatted_state(self):
            return f"""x = {self.state[0]}
theta_0 = {self.state[1]}
theta_0_dot = {self.state[2]}
is_at_edge = L: {self.is_near_left_end_stop()} R: {self.is_near_right_end_stop()}
current_power = {self.current_action}
reward = {self.reward}
tip = {self.tip_pos()}
dist_pen = {self.dist_penalty}
vel_pen = {self.vel_penalty }
"""
    def is_near_left_end_stop(self):
        return self.state[0] < -self.ENDSTOP_DIST
    def is_near_right_end_stop(self):
        return self.state[0] > self.ENDSTOP_DIST
    def render(self):
        pass
    def set_motor(self, target_power, limits=True):
        '''target_power: value between -1 and 1'''
        target_power = np.clip(target_power, -1, 1)
        if limits and self.is_near_left_end_stop():
            target_power = np.clip(target_power, 0, 1)
        elif limits and self.is_near_right_end_stop():
            target_power = np.clip(target_power, -1, 0)
        self.current_action = target_power
        target_converted = int((target_power+1)*2048)
        jrk2cmd('--target', str(target_converted))