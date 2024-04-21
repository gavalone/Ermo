import json
import random
import socket
from threading import Thread
import logging
import hashlib

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
                    handlers=[logging.FileHandler("logs/server.log"), logging.StreamHandler()], level=logging.INFO)

USERS = {}
CONNECTIONS_LIST = []
SALT = 'random_salt'.encode('utf-8')
COLORS = ['\33[31m', '\33[32m', '\33[33m', '\33[34m', '\33[35m', '\33[36m', '\33[91m', '\33[92m', '\33[93m', '\33[94m',
          '\33[95m', '\33[96m']


class ClientThread(Thread):
    def __init__(self, connection, address):
        super().__init__(daemon=True)
        self.connected = True
        self.conn = connection
        self.addr = address
        self.username = None
        self.color = random.choice(COLORS)
        self.login()

    def login(self):
        self.send_msg('Введите имя пользователя')
        name = self.receive_msg()
        self.username = name
        if name in USERS.keys():
            self.send_msg('Enter password')
            if USERS[name]['password'] == get_password_hash(self.receive_msg()):
                self.success_login()
            else:
                self.close_connection('incorrect password')
        else:
            self.send_msg('Set new password')
            USERS.update({name: {'password': get_password_hash(self.receive_msg())}})
            save_users()

    def success_login(self):
        self.send_msg(f'Success login')
        save_users()

    def close_connection(self, reason=''):
        logging.info(f'Connection closed {self.addr} {" - " + reason if reason else ""}')
        self.connected = False
        send_msg_all(f"{self.username} покинул чат")
        if self in CONNECTIONS_LIST:
            CONNECTIONS_LIST.remove(self)

    def send_msg(self, message):
        if self.connected:
            send_text(self.conn, message)

    def receive_msg(self):
        if not self.connected:
            return
        try:
            return receive_text(self.conn)
        except ConnectionResetError:
            self.close_connection('connection error')

    def run(self):
        CONNECTIONS_LIST.append(self)
        self.send_msg(f'{self.username}, welcome to chat')
        service_msg(self, 'joined the chat')

        while True and self.connected:
            message = self.receive_msg()
            if message == 'exit':
                self.close_connection('user exit')
                break
            send_msg_all(f'{self.color}{self.username}\33[0m: {message}')


def save_users():
    with open('users.json', 'w') as f:
        json.dump(USERS, f, indent=4)


def send_msg_all(message):
    [i.send_msg(message) for i in CONNECTIONS_LIST]


def service_msg(user, message):
    [i.send_msg(f'\33[4m{user.username} {message}\33[0m') for i in CONNECTIONS_LIST if i != user]


def get_password_hash(password):
    return hashlib.sha512(password.encode('utf-8') + SALT).hexdigest()


def receive_text(conn):
    return conn.recv(1024).decode('utf-8')


def send_text(conn, message):
    message = message.encode('utf-8')
    conn.send(message)


if __name__ == '__main__':
    sock = socket.socket()
    port = 9000
    while True:
        try:
            sock.bind(('', port))
            break
        except OSError:
            port += 1
    print(f'Started on {socket.gethostbyname(socket.gethostname())}:{port}')
    logging.info(f'Started on {socket.gethostbyname(socket.gethostname())}:{port}')
    sock.listen(10)
    try:
        with open('users.json', 'r') as file:
            USERS = json.load(file)
    except json.decoder.JSONDecodeError:
        USERS = {}
    while True:
        # Создать новые потоки для пользователей
        conn, addr = sock.accept()
        print(f'Opening connection {addr} ')
        logging.info(f'Opening connection {addr} ')
        thread = ClientThread(conn, addr)
        thread.start()