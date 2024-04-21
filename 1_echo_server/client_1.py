import socket

sock = socket.socket()
sock.connect(('localhost', 9999))
sock.send('hello, world!'.encode())

data = sock.recv(1024).decode()
sock.close()

print(data)