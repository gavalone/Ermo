import socket
from concurrent.futures import ThreadPoolExecutor



def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        decoded = data.decode()
        client_socket.send(b'Hi ' + decoded.encode())

    client_socket.close()

sock = socket.socket()
sock.bind(('', 9090))
sock.listen(0)
# print(sock.getsockname())

with ThreadPoolExecutor(max_workers=3) as executor:
    while True:
        conn, addr = sock.accept()
        print(f'Connected: {addr}')
        executor.submit(handle_client, conn)