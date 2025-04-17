import socket
import time

client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
client_socket.connect(('bbff::11', 12345))

count = 1
while True:
    data = f'Message {count}'
    client_socket.send(data.encode())
    print(data)
    count += 1
    time.sleep(2)

