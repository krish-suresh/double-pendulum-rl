'''
This file adapted from: https://github.com/georgesung/TD3
All I've done is make it a little messier and add in working with the Isaac Simulator.

I also modified TD3.py a tiny amount.


.././python.sh TD3-Bittle-16-1.py

'''


from __future__ import division
import torch
import gc
from collections import deque
import os
import numpy as np
import utils
import TD3
import argparse
import time
from pendulum import Pendulum
import cv2


LOAD_MODEL = False # or model name, like: "38-episode-384" 
MAX_EPISODES = 100
MAX_STEPS = 100
BITTLE_MOVE_DEQUESIZE = 10


HM_RANDOM_EPISODES = 10
MAX_BUFFER = 1_000_000   
MAX_TOTAL_REWARD = 300

parser = argparse.ArgumentParser()
parser.add_argument("--policy_name", default="TD3")					# Policy name
parser.add_argument("--env_name", default="BittleTD3")			    # OpenAI gym environment name
parser.add_argument("--seed", default=0, type=int)					# Sets Gym, PyTorch and Numpy seeds
parser.add_argument("--start_timesteps", default=1e4, type=int)		# How many time steps purely random policy is run for
parser.add_argument("--eval_freq", default=5e3, type=float)			# How often (time steps) we evaluate
parser.add_argument("--max_timesteps", default=1e9, type=float)		# Max time steps to run environment for
parser.add_argument("--save_models", action="store_true")			# Whether or not models are saved
parser.add_argument("--expl_noise", default=0.1, type=float)		# Std of Gaussian exploration noise
parser.add_argument("--batch_size", default=512, type=int)			# Batch size for both actor and critic
parser.add_argument("--discount", default=0.99, type=float)			# Discount factor 
parser.add_argument("--tau", default=0.005, type=float)				# Target network update rate
parser.add_argument("--policy_noise", default=0.2, type=float)		# Noise added to target policy during critic update
parser.add_argument("--noise_clip", default=0.5, type=float)		# Range to clip target policy noise
parser.add_argument("--policy_freq", default=2, type=int)			# Frequency of delayed policy updates
args = parser.parse_args()

file_name = "%s_%s_%s" % (args.policy_name, args.env_name, str(args.seed))
print("---------------------------------------")
print("Settings: %s" % (file_name))
print("---------------------------------------")

if not os.path.exists("results"):
    os.makedirs("results")
if args.save_models and not os.path.exists("pytorch_models"):
    os.makedirs("pytorch_models")

torch.manual_seed(args.seed)
np.random.seed(args.seed)

state_dim = 6 #env.observation_space.shape[0]
action_dim = 1 #env.action_space.shape[0] 
max_action = 0.5 #float(env.action_space.high[0])

if args.policy_name == "TD3": policy = TD3.TD3(state_dim, action_dim, max_action)

if LOAD_MODEL:
    policy.load(LOAD_MODEL,"models")


replay_buffer = utils.ReplayBuffer(max_size=MAX_BUFFER)
recent_rewards = deque()


with open("exploit_rwd.txt","w") as f:
    pass

with open("train_rwd.txt","w") as f:
    pass


largest_average_rwd = 0

pendulum = Pendulum()
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
CAMERA_CAPTURE_FPS = 60
CAMERA_CAPTURE_WIDTH = 1280
CAMERA_CAPTURE_HEIGHT = 720
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_EXPOSURE, -5) 
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CAPTURE_WIDTH)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CAPTURE_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAMERA_CAPTURE_FPS)
print("cam started")
while not pendulum.state():
    ret, frame = cap.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pendulum.update_state(hsv)
print("pendulum detected")
# while True:
#     ret, frame = cap.read()
#     
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#     pendulum.update_state(hsv)
#     for c in [pendulum.slide_marker.c, pendulum.joint_0_marker.c, pendulum.joint_1_marker.c, pendulum.left_end_marker.c, pendulum.right_end_marker.c]:
#         if c is not None:
#             cv2.drawContours(frame, c, -1, (0,255,0), 3)
#     cv2.imshow('frame', frame)
#     print(pendulum.reward())
#     key = cv2.waitKey(1) & 0xFF
#     if key == 27:
#         break
for _ep in range(MAX_EPISODES):
    if _ep < HM_RANDOM_EPISODES:
        do_random = True
    else:
        do_random = False
    if do_random: print("Random episode!")

    print('EPISODE :- ', _ep)
    bittle_starting_poses = {}
    prev_reward = 0
    bittle_states = {}
    bittle_actions = {}
    bittle_action_hist = {}
    ret, frame = cap.read()
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pendulum.update_state(hsv)

    for step in range(MAX_STEPS):
        print(f'Step: {step}')
        if step == 0:
            prev_reward = 0
            action_hist = deque(maxlen=BITTLE_MOVE_DEQUESIZE)

        ret, frame = cap.read()
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        pendulum.update_state(hsv)
        # if pendulum.is_near_left_end_stop() or pendulum.is_near_right_end_stop():
        #     break
        observation = np.asarray(pendulum.state())
        state = np.float32(observation)
        for c in [pendulum.slide_marker.c, pendulum.joint_0_marker.c, pendulum.joint_1_marker.c, pendulum.left_end_marker.c, pendulum.right_end_marker.c]:
            if c is not None:
                cv2.drawContours(frame, c, -1, (0,255,0), 3)
        cv2.imshow('frame', frame)
        if not do_random and _ep % 10 == 0:
            # TD3 exploit:
            action = policy.select_action(observation)
        else:
            if do_random:  
                action = np.random.randn(action_dim).clip(-max_action, max_action)

            else:
                action = policy.select_action(observation)
                if args.expl_noise != 0: 
                    action = (action + np.random.normal(0, args.expl_noise, size=action_dim)).clip(-max_action, max_action)

        print(f"action: {action}")
        action_hist.append(action)

        pendulum.set_motor(action)

        ret, frame = cap.read()
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        pendulum.update_state(hsv)

        
        total_reward = pendulum.reward()
        reward = total_reward - prev_reward

        prev_reward = total_reward
        new_state = np.float32(pendulum.state())

        replay_buffer.add((state, new_state, action, reward, 0)) 

        if step == MAX_STEPS-1:
            recent_rewards.append(total_reward)
    pendulum.set_motor(0)
    
    policy.train(replay_buffer, int((MAX_STEPS)/4), args.batch_size, args.discount, args.tau, args.policy_noise, args.noise_clip, args.policy_freq)


    gc.collect()
    recent_rewards.append(total_reward)
    print(f"average score: {np.mean(recent_rewards)}. memory size: {len(replay_buffer.storage)}")

    if not do_random and _ep % 3 == 0:
        print("Saving exploited reward statuts.")
        with open("exploit_rwd.txt","a") as f:
            f.write(f"{_ep},{int(np.mean(recent_rewards))}\n")
        policy.save(f"{int(np.mean(recent_rewards))}-episode-{_ep}", "models")

    else:
        with open("train_rwd.txt","a") as f:
            f.write(f"{_ep},{int(np.mean(recent_rewards))}\n")