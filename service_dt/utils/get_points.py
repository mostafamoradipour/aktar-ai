# importing the module
import cv2
import numpy as np


# function to display the coordinates of
# of the points clicked on the image
points = []
number = 0
def click_event(event, x, y, flags, params):
    global number
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)
        points.append([x, y])
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        number += 1
        cv2.putText(img, str(number), (x, y), font, 0.7, (255, 0, 0), 2)
        cv2.circle(img, (x, y), 2, (0, 0 , 255), 2, -1)
        cv2.imshow('image', img)


# driver function
if __name__ == "__main__":

    camera = cv2.VideoCapture('rtsp://192.168.1.103:554/user=admin&password=&channel=2&stream=0.sdp?real_stream--rtp-caching=800')
    ret, img = camera.read()
    
    cv2.imwrite('cam_view.jpg', img)

    # displaying the image
    cv2.imshow('image', img)
 
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback('image', click_event)

    # wait for a key to be pressed to exit
    cv2.waitKey(0)

    # save image points
    np.save('imagePoints.npy', np.array(points, dtype='float32'))

    # close the window
    cv2.destroyAllWindows()
