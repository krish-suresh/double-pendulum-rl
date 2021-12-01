from marker import Marker
import cv2
import numpy as np
vid = cv2.VideoCapture(0)
mouseX,mouseY = 0,0
marker_0 = Marker([90, 90,0],[120, 255,255])
marker_1 = Marker([15, 60, 100],[30, 255, 255])
marker_2 = Marker([170, 150, 50],[180, 255, 255], second_low=[0, 150, 50], second_high=[10, 255, 255])
marker_end = Marker([30, 60, 100],[60, 255, 255])

def update_mouse(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseX,mouseY = x,y
cv2.namedWindow('frame')
cv2.setMouseCallback('frame',update_mouse)

while(True):
      
    ret, frame = vid.read()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if mouseX:
        print(hsv[mouseX, mouseY])
        mouseX = None
    marker_0.update_position(hsv)
    marker_1.update_position(hsv)
    marker_2.update_position(hsv)
    left_blocked = cv2.rectangle(hsv, (int(hsv.shape[1]/2), 0), (hsv.shape[1], hsv.shape[0]), (0,0,0), -1)
    marker_end.update_position(left_blocked)
    # cv2.imshow('marker mask 0', marker_0.mask)
    # cv2.imshow('marker mask 1', marker_1.mask)
    # cv2.imshow('marker mask 2', marker_2.mask)
    cv2.imshow('marker mask end', marker_end.mask)
    for c in [marker_0.c, marker_1.c, marker_2.c, marker_end.c]:
        if c is not None:
            cv2.drawContours(frame, c, -1, (0,255,0), 3)
    cv2.imshow('frame', frame)

    # print(marker_0.pos())
    if cv2.waitKey(1) & 0xFF == ord('g'):
        print (f"Green {str(marker_0.hsv_low)} to {str(marker_0.hsv_high)}")
        marker_0.hsv_low = np.array([int(x) for x in input("Green Low: ").split(' ')])
        marker_0.hsv_high = np.array([int(x) for x in input("Green High: ").split(' ')])
    if cv2.waitKey(1) & 0xFF == ord('r'):
        print (f"Red {str(marker_2.hsv_low)} to {str(marker_2.hsv_high)}")
        marker_2.hsv_low = [int(x) for x in input("Red Low: ").split(' ')]
        marker_2.hsv_high = [int(x) for x in input("Red High: ").split(' ')]
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
vid.release()
cv2.destroyAllWindows()