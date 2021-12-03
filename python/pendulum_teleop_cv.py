from pendulum import Pendulum
import cv2
vid = cv2.VideoCapture(0)
pendulum = Pendulum()

cv2.namedWindow('frame')
while True:
    ret, frame = vid.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pendulum.update_state(hsv)
    for c in [pendulum.slide_marker.c, pendulum.joint_0_marker.c, pendulum.joint_1_marker.c, pendulum.left_end_marker.c, pendulum.right_end_marker.c]:
        if c is not None:
            cv2.drawContours(frame, c, -1, (0,255,0), 3)
    cv2.imshow('frame', frame)

    print(pendulum.formatted_state(), end='\r')

    key = cv2.waitKey(1) & 0xFF
    # if the 'ESC' key is pressed, Quit
    if key == 27:
        break
    if key == 100: # D
        pendulum.set_motor(0.5, limits=True)
    elif key == 97:# A
        pendulum.set_motor(-0.5, limits=True)
    else:
        pendulum.set_motor(0, limits=True)

vid.release()
cv2.destroyAllWindows()