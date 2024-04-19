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
path=os.path.join(os.path.abspath(os.curdir) , 'my_model.onnx')
args_confidence = 0.2

# initialize the list of class labels 
CLASSES = ['KLUBNIKA', 'raspberry']

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromONNX (path)
########################

def video_stream():
	
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

		cv2.imshow("RECEIVING VIDEO",frame)
		key = cv2.waitKey(1) & 0xFF
	
		if key == ord('q'):
			client_socket.close()
			os._exit(1)
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





from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=2) as executor:
	executor.submit(video_stream)

