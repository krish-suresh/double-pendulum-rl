from marker import Marker
import cv2
import numpy as np
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
CAMERA_CAPTURE_FPS = 60
CAMERA_CAPTURE_WIDTH = 1280
CAMERA_CAPTURE_HEIGHT = 720
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
cap.set(cv2.CAP_PROP_EXPOSURE, -5) 
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CAPTURE_WIDTH)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CAPTURE_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, CAMERA_CAPTURE_FPS)
mouseX,mouseY = 0,0
marker_0 = Marker([90, 150,130],[130, 255,255])
marker_1 = Marker([40, 30, 100],[70, 255, 255])
marker_2 = Marker( [170, 130, 70],[180, 255, 255], second_low=[0, 180, 130], second_high=[5, 255, 255])
marker_end = Marker([150, 70, 130],[170, 255, 255])

def update_mouse(event,x,y,flags,param):
    global mouseX,mouseY
    if event == cv2.EVENT_LBUTTONDBLCLK:
        mouseX,mouseY = x,y
cv2.namedWindow('frame')
cv2.setMouseCallback('frame',update_mouse)
i=0
while(True):
      
    ret, frame = cap.read()
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    # frame = cv2.imread('python/images/102.png')
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if mouseX:
        print(hsv[mouseY, mouseX])
        mouseX = None
    marker_0.update_position(hsv)
    marker_1.update_position(hsv)
    marker_2.update_position(hsv)
    left_blocked = cv2.rectangle(hsv, (int(hsv.shape[1]/2), 0), (hsv.shape[1], hsv.shape[0]), (0,0,0), -1)
    marker_end.update_position(left_blocked)
    cv2.imshow('marker mask 0', marker_0.mask)
    # cv2.imshow('marker mask 1', marker_1.mask)
    # cv2.imshow('marker mask 2', marker_2.mask)
    # cv2.imshow('marker mask end', marker_end.mask)
    for c in [marker_0.c, marker_1.c, marker_2.c, marker_end.c]:
        if c is not None:
            cv2.drawContours(frame, c, -1, (0,255,0), 3)
    cv2.imshow('frame', frame)
    # cv2.imwrite(f'python/images/{i}.png', frame)
    i+=1
    # print(marker_0.pos())
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
cap.release()
cv2.destroyAllWindows()