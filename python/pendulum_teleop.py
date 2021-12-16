from pendulum import Pendulum
import cv2

pendulum = Pendulum()

cv2.namedWindow('frame')
while True:
    key = cv2.waitKey(1) & 0xFF

    # if the 'ESC' key is pressed, Quit
    if key == 27:
        quit()
    if key == 97:
        pendulum.set_motor(1, limits=False)
    elif key == 100:
        pendulum.set_motor(-1, limits=False)
    elif key == 115:
        pendulum.set_motor(0, limits=False)
    elif key != 255:
        print(key)