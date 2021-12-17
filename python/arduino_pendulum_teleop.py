from arduino_pendulum import Pendulum
import cv2

pendulum = Pendulum()

cv2.namedWindow('frame')
motor = 0
while True:
    key = cv2.waitKey(1) & 0xFF
    
    print(pendulum.formatted_state())
    # if the 'ESC' key is pressed, Quit
    if key == 27:
        quit()
    if key == 97:
        motor = -0.3
    elif key == 100:
        motor = 0.3
    elif key == 115:
        motor = 0
    elif key != 255:
        print(key)
    pendulum.step(motor)
    # print(pendulum.tip_pos())