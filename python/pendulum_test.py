from pendulum import Pendulum
import cv2
import numpy as np
vid = cv2.VideoCapture(0)

pendulum = Pendulum()


while(True):
      
    ret, frame = vid.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pendulum.update_state(hsv)
    cv2.imshow('marker mask 0', pendulum.left_end_marker.mask)
    # cv2.imshow('marker mask 1', marker_1.mask)
    # cv2.imshow('marker mask 2', marker_2.mask)
    # cv2.imshow('marker mask end', marker_end.mask)
    for c in [pendulum.slide_marker.c, pendulum.joint_0_marker.c, pendulum.joint_1_marker.c, pendulum.left_end_marker.c, pendulum.right_end_marker.c]:
        if c is not None:
            cv2.drawContours(frame, c, -1, (0,255,0), 3)
    cv2.imshow('frame', frame)


    print(pendulum.formatted_state(), end='\r')
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
vid.release()
cv2.destroyAllWindows()