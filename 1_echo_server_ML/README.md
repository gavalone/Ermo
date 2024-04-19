## Добавляем в echo-server распознавание объектов

Функционал добавлял в файл viclient.py и viclient-box.py

В первом используем простую модель

Во втором, модель посложнее и добавлено детектирование распознаваемого объекта, поэтому слабый компьютер может и непотянуть.


___Файлы:_________________________________________________________________________________________________________
My_first_CV_classification.ipynb
   - Jupyter notebook for training two models using PyTorch
__________________________________________________________________________________  

webonnx.py and rt_object_class_PTH_resnet18.py
 - Scripts for classifying images using the OpenCV webcam and corresponding neural network models
__________________________________________________________________________________  

my_model.onnx and my_resnet18.onnx

- Models for classifying two classes: arduino and raspberry
______________________
MobileNetSSD_deploy.caffemodel
 - модель нескольких объектов "background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"
______________
Почитать дополнительно:
  https://habr.com/ru/post/478208/

https://proglib.io/p/real-time-object-detection

https://pyimagesearch.com/2017/09/18/real-time-object-detection-with-deep-learning-and-opencv/?utm_source=mybridge&utm_medium=blog&utm_campaign=read_more

https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html