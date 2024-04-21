import socket
sock = socket.socket()
try:
  sock.bind(('', 80))
except OSError:
  sock.bind(('', 8080))
sock.listen(5)
conn, addr = sock.accept()
print("Connected", addr)
conn.close()
'''

Сессия HTTP состоит из запроса клиента и ответа сервера. Запустив наш сервер, мы можем попробовать подключиться к нему из браузера. Запустим браузер и наберем в адресной строке адрес хоста и номер порта в таком виде: “localhost:8080”. Мы должны увидеть, что сервер напечатал сообщение о подключении.

Теперь давайте посмотрим, что браузер отправляет в сокет:

'''
conn, addr = sock.accept()
print("Connected", addr)
data = conn.recv(8192)
msg = data.decode()
print(msg)

msg = data.decode()
print(msg)
resp = """HTTP/1.1 200 OK
Hello, webworld!"""
conn.send(resp.encode())
conn.close()