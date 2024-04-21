import socket
import re
import os

HOST = 'localhost'
PORT = 9090
END_FLAG = b"$$STREAM_FILE_END_FLAG$$"
FAIL_FLAG = b'$FAILED$'

# login = input("Введите логин: ")
# password = input("Введите пароль: ")

login = "admin"
password = "admin"
current_directory = "\\"

# Функция создания сообщения для отправки на сервер
def creator(message, size=0):
    global login, password, current_directory
    return f"{login}=login{password}=password{current_directory}=cur_dir{size}=file_size{message}".encode()

# Функция для приема файла от сервера
def receiving(request, sock):
    global FAIL_FLAG, END_FLAG
    flag_finder = sock.recv(1024)
    if FAIL_FLAG in flag_finder:
        print((flag_finder.replace(FAIL_FLAG, b"")).decode())
    else:
        filename = re.split("[ \\/]+", request)[-1]
        with open(filename, "wb") as bytefile:
            while True:
                if END_FLAG in flag_finder:
                    bytefile.write(flag_finder.replace(END_FLAG, b""))
                    break
                else:
                    bytefile.write(flag_finder)
                    flag_finder = sock.recv(1024)

# Функция для отправки файла на сервер
def sending(request, sock):
    global END_FLAG
    filename = re.split("[ \\/]+", request)[-1]
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        sock.send(creator(request, size))
        enough_flag = sock.recv(1024).decode()
        if enough_flag != '$ENOUGHT$':
            print(enough_flag)
            return
        with open(filename, "rb") as bytefile:
            while read_bytes := bytefile.read(1024):
                sock.send(read_bytes)
        sock.send(END_FLAG)
    else:
        print("Нет такого файла")

sock = socket.socket()
try:
    sock.connect((HOST, PORT))
    while True:
        try:
            request = input(current_directory + '>')
            request = request.strip()
            if request == "exit":
                print("goodbye")
                break
            if request[:9] == "send_file":
                if request == "send_file":
                    print("Нет такого файла")
                else:
                    sending(request, sock)
            else:
                sock.send(creator(request))
                if request[:9] == "get_file " or request == "get_file":
                    receiving(request, sock)
                else:
                    response = sock.recv(1024).decode()
                    if request[:3] == "cd " or request == "cd":
                        current_directory = response
                    else:
                        print(response)
        except KeyboardInterrupt:
            print("Процесс завершен по запросу пользователя")
            break
finally:
    sock.close()
