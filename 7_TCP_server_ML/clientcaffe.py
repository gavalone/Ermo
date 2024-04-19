# Welcome to PyShine
# This is client code to receive video and audio frames over UDP/TCP

import cv2, imutils, socket
import numpy as np
import time, os
import base64
import threading, wave, pickle,struct
# For details visit pyshine.com
BUFF_SIZE = 65536

BREAK = False
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '127.0.0.1'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9688
message = b'Hello'

client_socket.sendto(message,(host_ip,port))
#--------onnx----
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
net = cv2.dnn.readNetFromCaffe(txt, caffemodel)
########################


	
cv2.namedWindow('RECEIVING VIDEO')        
cv2.moveWindow('RECEIVING VIDEO', 10,360) 
fps,st,frames_to_count,cnt = (0,0,20,0)
while True:
	packet,_ = client_socket.recvfrom(BUFF_SIZE)
	data = base64.b64decode(packet,' /')
	npdata = np.fromstring(data,dtype=np.uint8)

	frame = cv2.imdecode(npdata,1)
	frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
	frame = imutils.resize(frame, width=400)
	(h, w) = frame.shape[:2]
	# grab the frame dimensions and convert it to a blob
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),0.007843, (300, 300), 127.5)
	cv2.imshow("Cropped image", cv2.resize(frame, (32, 32)))

	# pass the blob through the network and obtain the detections and
	# predictions
	net.setInput(blob)
	detections = net.forward()
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

			if cnt == frames_to_count:
				try:
					fps = round(frames_to_count/(time.time()-st))
					st=time.time()
					cnt=0
				except:
					pass
			cnt+=1
	
		
client_socket.close()
cv2.destroyAllWindows() 



