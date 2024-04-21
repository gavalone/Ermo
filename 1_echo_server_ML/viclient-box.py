import socket, cv2, pickle, struct

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2
import os

# path=os.path.join(os.path.abspath(os.curdir) , 'my_model.onnx')
caffemodel=os.path.join(os.path.abspath(os.curdir) , 'MobileNetSSD_deploy.caffemodel')
txt=os.path.join(os.path.abspath(os.curdir) , 'MobileNetSSD_deploy.prototxt.txt')
args_confidence = 0.2

# initialize the list of class labels 
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
# load our serialized model from disk
print("[INFO] loading model...")
# net = cv2.dnn.readNetFromONNX (path)
net = cv2.dnn.readNetFromCaffe(txt, caffemodel)
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
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)
    # pass the blob through the network and obtain the detections and
    # predictions
    net.setInput(blob)
    detections = net.forward()
    # extract the confidence (i.e., probability) associated with
    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence
        if confidence > args_confidence:
        # extract the index of the class label from the
        # `detections`, then compute the (x, y)-coordinates of
        # the bounding box for the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # draw the prediction on the frame
            label = "{}: {:.2f}%".format(CLASSES[idx],confidence * 100)
            cv2.rectangle(frame, (startX, startY), (endX, endY),COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
    
            cv2.imshow("RECEIVING VIDEO",frame)
            key = cv2.waitKey(1) & 0xFF
            if key  == ord('q'):
                break
sock.close()
cv2.destroyAllWindows()
