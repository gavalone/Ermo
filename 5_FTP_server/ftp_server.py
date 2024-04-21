import json
import logging
import os
import shutil
import socket
import re

# Настройка логгера
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

END_FLAG = b"$$STREAM_FILE_END_FLAG$$"
FAIL_FLAG = b'$FAILED$'
PORT = 9090
global_root = os.path.join(os.getcwd())
usersfile = os.path.join(global_root, "users.json")
log_file = os.path.join(global_root, "log.txt")


def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def log_print(*strings):
    message = " ".join([str(item) for item in strings])
    print(message)  # Для вывода на консоль (необязательно)
    logger.info(message)  # Для записи в лог-файл


def load_users():
    try:
        with open(usersfile, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_users(users_data):
    with open(usersfile, "w") as file:
        json.dump(users_data, file, indent=4)


def authorization(message):
    global global_root
    users_data = load_users()

    login, message = message.split("=login", 1)
    password, message = message.split("=password", 1)
    current_directory, message = message.split("=cur_dir", 1)
    size, message = message.split("=file_size", 1)

    if login == password == "admin":
        user_root = global_root
    else:
        user_root = os.path.join(global_root, login)

        if login in users_data and users_data[login]["password"] == password:
            pass
        else:
            users_data[login] = {"password": password}
            save_users(users_data)

        try:
            os.makedirs(user_root)
            log_print(f"Создана директория пользователя: {user_root}")
        except FileExistsError:
            pass

    return user_root, current_directory, message, size


def process(req):
    req = authorization(req)
    if req:
        user_root, current_directory, req, size = req
        try:
            req, *dir_ = req.split()
        except ValueError:
            path = ""
        else:
            path = [path_decoder(user_root, current_directory, item) for item in dir_]

        if req == 'pwd':
            return pwd(current_directory)
        elif req == 'ls':
            return ls(os.path.join(user_root, current_directory[1:]))
        elif req == "cd":
            return cd(path[0], current_directory, user_root)
        elif req == 'mkdir':
            return mkdir(path[0])
        elif req == 'rmtree':
            return rmtree(path[0])
        elif req == 'touch':
            return touch(path[0])
        elif req == 'remove':
            return remove(path[0])
        elif req == 'cat':
            return cat(path[0])
        elif req == 'rename':
            return rename(*path[:2])
        elif req == "get_file":
            return get_file(path[0])
        elif req == "send_file":
            return send_file(path[0], user_root, size)

        else:
            return 'Некорректный запрос'
    else:
        return "Неверный пароль"


def path_decoder(root, current, dir_):
    if current == "\\" and dir_[:2] == "..":
        return os.path.join(root, dir_[2:])
    elif dir_[0] in ["\\", "/"]:
        dir_ = re.sub(r"^[\\/]+", "", dir_)
        log_print(dir_)
        return os.path.join(root, dir_)
    else:
        return os.path.join(root, current[1:], dir_)


def handle_exceptions(path_func):
    def wrapper(*path):
        try:
            returned = path_func(*path)
            if returned is None:
                return "Успешно"
            else:
                return returned
        except FileNotFoundError:
            return 'Неверный путь'
        except FileExistsError:
            return 'Уже существует'
        except PermissionError:
            return "Доступ запрещен"

    return wrapper



def pwd(dirname):
    return os.path.join(dirname)


def ls(path):
    return '\n\r'.join(os.listdir(path))


def cd(path, current, root):
    try:
        os.chdir(path)
        log_print(f"Переход в директорию: {path}")
    except:
        return current
    return os.getcwd().replace(root, "") + "\\"


@handle_exceptions
def mkdir(path):
    os.makedirs(path)
    log_print(f"Создана директория: {path}")


@handle_exceptions
def rmtree(path):
    shutil.rmtree(path)
    log_print(f"Удалена директория: {path}")


@handle_exceptions
def remove(path):
    os.remove(path)
    log_print(f"Удален файл: {path}")


@handle_exceptions
def touch(path):
    with open(path, 'x'):
        pass
    log_print(f"Создан пустой файл: {path}")


@handle_exceptions
def cat(path):
    with open(path, "r") as file:
        return "\n\r".join(file.readlines())


@handle_exceptions
def rename(path1, path2):
    os.rename(path1, path2)
    log_print(f"Файл или директория переименована: {path1} -> {path2}")


def get_file(path):
    global conn, END_FLAG, FAIL_FLAG
    try:
        with open(path, "rb") as bytefile:
            while read_bytes := bytefile.read(1024):
                conn.send(read_bytes)
    except FileNotFoundError:
        returned = 'Неверный путь'.encode() + FAIL_FLAG
    except PermissionError:
        returned = 'Доступ запрещен'.encode() + FAIL_FLAG
    else:
        returned = END_FLAG
    log_print("Файл был отправлен")
    return returned


def send_file(path, root, size):
    global conn, END_FLAG, FAIL_FLAG
    available = pow(2, 20) * 10 - get_size(root)  # 10Мб для каждого пользователя
    print(available, int(size))
    if available < int(size):
        return "Недостаточно места на диске!"
    else:
        conn.send("$ДОСТАТОЧНО$".encode())
    flag_finder = conn.recv(1024)
    with open(path, "wb") as bytefile:
        while True:
            if END_FLAG in flag_finder:
                bytefile.write(flag_finder.replace(END_FLAG, b""))
                break
            else:
                bytefile.write(flag_finder)
                flag_finder = conn.recv(1024)
    log_print("Файл был получен")
    return "Загружен успешно"


sock = socket.socket()
sock.bind(('', PORT))
sock.listen()
log_print("Прослушиваем порт", PORT)

try:
    while True:
        conn, addr = sock.accept()
        request = conn.recv(1024).decode()
        log_print("Получен запрос:", request)
        response = process(request)
        log_print("Ответ:", response)
        if not response:
            response = "\00"
        try:
            conn.send(response.encode())
        except AttributeError:
            conn.send(response)
        log_print("Ответ отправлен")
        conn.close()
except KeyboardInterrupt:
    log_print("Процесс завершен по запросу пользователя")
    sock.close()
