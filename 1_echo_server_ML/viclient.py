import socket, cv2, pickle, struct

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2
import os

path=os.path.join(os.path.abspath(os.curdir) , 'my_model.onnx')
args_confidence = 0.2

# initialize the list of class labels 
CLASSES = ['KLUBNIKA', 'raspberry']

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromONNX (path)

# create socket
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

sock.connect(('127.0.0.1',9090))

data = b""
payload_size = struct.calcsize("Q")

while True:
    while len(data) < payload_size:
        packet = sock.recv(4*1024) 
        if not packet: break
        data+=packet
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("Q",packed_msg_size)[0]
    while len(data) < msg_size:
        data += sock.recv(4*1024)
    frame_data = data[:msg_size]
    data  = data[msg_size:]
    frame = pickle.loads(frame_data)
    frame = imutils.resize(frame, width=400)
    # grab the frame dimensions and convert it to a blob
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (32, 32)),scalefactor=1.0/32
                              , size=(32, 32), mean= (128,128,128), swapRB=True)
    cv2.imshow("Cropped image", cv2.resize(frame, (32, 32)))

    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()
    print(list(zip(CLASSES,detections[0])))
    # loop over the detections
    # extract the confidence (i.e., probability) associated with
    # the prediction
    confidence = abs(detections[0][0]-detections[0][1])
    print("confidence = ", confidence)
    # filter out weak detections by ensuring the `confidence` is
    # greater than the minimum confidence
    if (confidence > args_confidence) :
        class_mark=np.argmax(detections)
        cv2.putText(frame, CLASSES[class_mark], (30,30),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (242, 230, 220), 2)
    # show the output frame

    cv2.imshow("RECEIVING VIDEO",frame)
    key = cv2.waitKey(1) & 0xFF
    if key  == ord('q'):
        break
sock.close()
cv2.destroyAllWindows()
