import socket
import threading

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

    def broadcast(self, message, sender_address):
        for client_socket, client_address in self.clients:
            if client_address != sender_address:
                try:
                    client_socket.send(f"{sender_address[0]}:{sender_address[1]} says: {message}".encode())
                except:
                    client_socket.close()
                    self.clients.remove((client_socket, client_address))


    def handle_client(self, client_socket, client_address):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"{client_address[0]}:{client_address[1]} says: {message}")
                    self.broadcast(message, client_address)
            except:
                continue

    def run(self):
        print(f"Server is listening on {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"New connection from {client_address}")
            self.clients.append((client_socket, client_address))
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

if __name__ == "__main__":
    server = ChatServer("localhost", 9090)
    server.run()
