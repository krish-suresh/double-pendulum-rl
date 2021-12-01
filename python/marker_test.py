from marker import Marker
import cv2
import numpy as np
vid = cv2.VideoCapture(0)
mouseX,mouseY = 0,0
marker_0 = Marker([15,100,100],[30, 200, 180])
marker_1 = Marker([0,90,60],[10, 130, 100])
marker_2 = Marker([120,60,60],[145, 120, 120])
def update_mouse(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseX,mouseY = x,y
cv2.namedWindow('frame')
cv2.setMouseCallback('frame',update_mouse)

while(True):
      
    ret, frame = vid.read()
    cv2.imshow('frame', frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if mouseX:
        print(hsv[mouseX, mouseY])
        mouseX = None
    marker_0.update_position(hsv)
    marker_1.update_position(hsv)
    marker_2.update_position(hsv)
    cv2.imshow('marker mask 0', marker_0.mask)
    cv2.imshow('marker mask 1', marker_1.mask)
    cv2.imshow('marker mask 2', marker_2.mask)
    # print(marker_0.pos())
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
vid.release()
cv2.destroyAllWindows()