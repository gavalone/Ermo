import socket
import threading

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_message(self):
        while True:
            message = input("")
            self.client_socket.send(message.encode())

    def receive_message(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    print(message)
            except:
                break

    def run(self):
        send_thread = threading.Thread(target=self.send_message)
        receive_thread = threading.Thread(target=self.receive_message)

        send_thread.start()
        receive_thread.start()

if __name__ == "__main__":
    client = ChatClient("localhost", 9090)
    client.run()
