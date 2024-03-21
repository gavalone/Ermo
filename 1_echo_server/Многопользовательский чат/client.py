import socket
import sys

def send_message(client_socket, message):
    message_bytes = message.encode()
    message_length = len(message_bytes).to_bytes(4, byteorder='big')
    client_socket.sendall(message_length + message_bytes)

server_host = input("Enter server host (default: localhost): ") or "localhost"
server_port = int(input("Enter server port (default: 12345): ") or 12345)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_port))

while True:
    message = input("Enter message (type 'exit' to quit): ")
    send_message(client_socket, message)
    if message == "exit":
        break

client_socket.close()