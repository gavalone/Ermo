import socket
import sys

def receive_message(client_socket):
    message_length = int.from_bytes(client_socket.recv(4), byteorder='big')
    message_bytes = client_socket.recv(message_length)
    return message_bytes.decode()

server_host = input("Enter server host (default: localhost): ") or "localhost"
server_port = int(input("Enter server port (default: 12345): ") or 12345)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_host, server_port))
server_socket.listen()

print(f"Server is listening on {server_host}:{server_port}")

while True:
    client_socket, client_address = server_socket.accept()
    print(f"Connection from {client_address}")

    while True:
        message = receive_message(client_socket)
        print(f"Received message: {message}")
        if message == "exit":
            break

    client_socket.close()