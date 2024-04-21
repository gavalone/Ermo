import socket
import re
import os

HOST = 'localhost'
PORT = 9090
END_FLAG = b"$$STREAM_FILE_END_FLAG$$"
FAIL_FLAG = b'$FAILED$'

# Логин и пароль для тестирования
login = password = 'Mashirov'

current_directory = "\\"

# Функция создания сообщения для отправки
def creator(message, size=0):
    global login, password, current_directory
    return f"{login}=login{password}=password{current_directory}=cur_dir{size}=file_size{message}".encode()

# Функция получения файла
def receiving(sock, request):
    global FAIL_FLAG, END_FLAG
    try:
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
    except Exception as e:
        print(f"Произошла ошибка при получении файла: {e}")

# Функция отправки файла
def sending(sock, request):
    global END_FLAG
    filename = re.split("[ \\/]+", request)[-1]
    if os.path.exists(filename):
        try:
            size = os.path.getsize(filename)
            sock.send(creator(request, size))
            enought_flag = sock.recv(1024).decode()
            if enought_flag != '$ENOUGHT$':
                print(enought_flag)
                return
            with open(filename, "rb") as bytefile:
                while read_bytes := bytefile.read(1024):
                    sock.send(read_bytes)
            sock.send(END_FLAG)
        except Exception as e:
            print(f"Произошла ошибка при отправке файла: {e}")
    else:
        print("Нет такого файла")

# Основная функция для выполнения команды
def main(command):
    global current_directory
    sock = socket.socket()
    print(">", command)
    request = command.strip()
    if request == "exit":
        print("goodbye")
        return

    try:
        sock.connect((HOST, PORT))
        if request[:9] == "send_file":
            if request == "send_file":
                print("Нет такого файла")
            else:
                sending(sock, request)
        else:
            sock.send(creator(request))
            if request[:9] == "get_file " or request == "get_file":
                receiving(sock, request)
            else:
                response = sock.recv(1024).decode()
                if request[:3] == "cd " or request == "cd":
                    current_directory = response
                else:
                    print(response)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        sock.close()

# Список команд для выполнения
commands = [
    "mkdir test1",
    "cd ...../test1",
    "cd ./test1",
    "mkdir ../test1/test11",
    "ls",
    "pwd",
    "rmtree test11",
    "ls",
    "touch 1.txt",
    "rename 1.txt 11.txt",
    "ls",
    "remove 1.txt",
    "cat 1.txt",
    "cat 11.txt",
    "cd ////",
    "pwd",
    "cd \\",
    "pwd",
    "rmtree test1",
    "ls"
]

# Итерация через команды и их выполнение
for command in commands:
    try:
        main(command)
    except:
        print('Некорректная работа!')
        raise
