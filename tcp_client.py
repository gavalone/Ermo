import socket

def get_host_port():
    # Запрос хоста и порта у пользователя
    host = input("Введите хост (по умолчанию 127.0.0.1): ").strip() or '127.0.0.1'
    port = input("Введите порт (по умолчанию 65432): ").strip() or 65432
    return host, int(port)

def echo_client():
    # Подключение к серверу
    host, port = get_host_port()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((host, port))
                print(f"Подключено к {host}:{port}")

                while True:
                    data = client_socket.recv(1024).decode()
                    print(data)  # Выводим сообщение от сервера
                    if "Введите ваше имя:" in data:
                        name = input().strip()
                        client_socket.sendall(name.encode())  # Отправляем имя серверу
                    elif "Введите пароль:" in data:
                        password = input().strip()
                        client_socket.sendall(password.encode())  # Отправляем пароль серверу
                    else:
                        break  # После отправки имени и пароля выходим из цикла ожидания ответа от сервера

                while True:
                    user_input = input("Введите сообщение для отправки на сервер (или 'exit' для выхода): ")
                    client_socket.sendall(user_input.encode())  # Отправляем сообщение серверу
                    if user_input.strip().lower() == "exit":
                        print("Отключение от сервера")
                        break
                    data = client_socket.recv(1024)
                    print(f"Получен ответ от сервера: {data.decode()}")

            except ConnectionRefusedError:
                print("Не удалось подключиться к серверу. Проверьте настройки сервера.")
    except ValueError:
        print("Ошибка ввода порта. Порт должен быть целым числом.")
    except KeyboardInterrupt:
        print("Программа остановлена по запросу пользователя.")

if __name__ == "__main__":
    echo_client()
