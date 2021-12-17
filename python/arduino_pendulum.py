import serial
import time
import subprocess
import numpy as np
import math
import time
import gym
from gym import spaces
from gym.utils import seeding

def jrk2cmd(*args):
  return subprocess.check_output(['jrk2cmd'] + list(args))
def angle_wrap(angle):
    return (angle + np.pi) % (2 * np.pi) - np.pi


class Pendulum(gym.Env):
    def __init__(self):
        self.arduino = serial.Serial('/dev/ttyACM0', 9600)
        self.ENDSTOP_DIST = 120 # mm
        self.state = None
        high = np.array([self.ENDSTOP_DIST, math.pi, math.pi], dtype=np.float32)
        self.action_space = spaces.Box(
            low=-1, high=1, shape=(1,), dtype=np.float32
        )
        self.observation_space = spaces.Box(low=-high, high=high, dtype=np.float32)
        self.current_action = 0

    def step(self, action, check_pos = False):
        # update marker positions
        line = self.arduino.readline()
        if line:
            a = line.decode("utf-8", "ignore").strip().split(',')
            if len(a) == 6:
                self.state = [float(x) for x in line.decode("utf-8", "replace").strip().split(',')]
        # if check_pos:
        #     if self.current_action != 0 and (self.is_near_left_end_stop() or self.is_near_left_end_stop()):
        #         self.set_motor(0)
        # else:
        self.set_motor(action)
    def reward(self):
        if not self.state:
            return 0
        return self.state # distance calc TODO
    def reset(self):
        input("[ENTER] when reset")
    def formatted_state(self):
        if self.state:
            return f"""x = {self.state[0]}
theta_0 = {self.state[1]}
theta_1 = {self.state[2]}
x_dot = {self.state[3]}
theta_0_dot = {self.state[4]}
theta_1_dot = {self.state[5]}
is_at_edge = L: {self.is_near_left_end_stop()} R: {self.is_near_right_end_stop()}
current_power= {self.current_action}
"""
        else:
            return None
    def is_near_left_end_stop(self):
        return self.state and self.state[0] > self.ENDSTOP_DIST
    def is_near_right_end_stop(self):
        return self.state and self.state[0] < -self.ENDSTOP_DIST

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