import socket
import logging
import json
import hashlib

def get_host_port():
    # Запрос хоста и порта у пользователя
    host = input("Введите хост (по умолчанию 127.0.0.1): ").strip() or '127.0.0.1'
    port = input("Введите порт (по умолчанию 65432): ").strip() or 65432
    return host, int(port)

def setup_logging():
    # Настройка логирования в файл
    logging.basicConfig(filename='server.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def find_available_port(host, start_port):
    # Поиск доступного порта
    port = start_port
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:
                temp_socket.bind((host, port))
            return port
        except OSError:
            port += 1

def load_known_clients():
    # Загрузка известных клиентов из файла JSON
    try:
        with open("known_clients.json", "r") as f:
            known_clients = json.load(f)
    except FileNotFoundError:
        known_clients = {}
    return known_clients

def save_known_client(ip_address, client_name, password):
    # Сохранение нового клиента в файл JSON с хешированным паролем
    known_clients = load_known_clients()
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    known_clients[ip_address] = {'name': client_name, 'password': hashed_password}
    with open("known_clients.json", "w") as f:
        json.dump(known_clients, f, ensure_ascii=False)

def echo_server():
    # Запуск сервера
    setup_logging()
    host, port = get_host_port()

    try:
        # Находим доступный порт
        port = find_available_port(host, port)
        print(f"Сервер запущен на {host}:{port}")
        logging.info(f"Сервер запущен на {host}:{port}")

        known_clients = load_known_clients()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((host, port))
            server_socket.listen(1)

            while True:
                conn, addr = server_socket.accept()
                logging.info(f"Подключился клиент {addr}")

                # Проверяем, знаком ли сервер с клиентом по его IP-адресу
                if addr[0] in known_clients:
                    client_data = known_clients[addr[0]]
                    client_name = client_data['name']
                    conn.sendall(f"Добро пожаловать, {client_name}!\n".encode())
                else:
                    conn.sendall("Введите ваше имя:\n".encode())
                    client_name = conn.recv(1024).decode().strip()

                    # Запрос пароля
                    conn.sendall("Введите пароль:\n".encode())
                    password = conn.recv(1024).decode().strip()

                    save_known_client(addr[0], client_name, password)
                    conn.sendall(f"Добро пожаловать, {client_name}!\n".encode())  # Отправляем приветствие после получения имени

                while True:
                    data = conn.recv(1024)
                    if not data:
                        logging.info("Клиент отключился")
                        break
                    message = data.decode()
                    logging.info(f"Получено: {message}")
                    if message.strip().lower() == "exit":
                        logging.info("Клиент запросил отключение")
                        break
                    conn.sendall(data)
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    echo_server()
