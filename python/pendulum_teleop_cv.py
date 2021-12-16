from pendulum import Pendulum
import cv2
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
CAMERA_CAPTURE_FPS = 60
CAMERA_CAPTURE_WIDTH = 1280
CAMERA_CAPTURE_HEIGHT = 720
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_EXPOSURE, -5) 
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CAPTURE_WIDTH)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CAPTURE_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAMERA_CAPTURE_FPS)

pendulum = Pendulum()

cv2.namedWindow('frame')
while True:
    ret, frame = cap.read()
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pendulum.update_state(hsv)
    for c in [pendulum.slide_marker.c, pendulum.joint_0_marker.c, pendulum.joint_1_marker.c, pendulum.left_end_marker.c, pendulum.right_end_marker.c]:
        if c is not None:
            cv2.drawContours(frame, c, -1, (0,255,0), 3)
    cv2.imshow('frame', frame)

    print(pendulum.formatted_state(), end='\r')
    # print(pendulum.reward())
    key = cv2.waitKey(1) & 0xFF
    # if the 'ESC' key is pressed, Quit
    if key == 27:
        break
    if key == 100: # D
        pendulum.set_motor(0.3)
    elif key == 97:# A
        pendulum.set_motor(-0.3)
    elif key == 115:
        pendulum.set_motor(0)
    elif key != 255:
        print(key)

cap.release()
cv2.destroyAllWindows()