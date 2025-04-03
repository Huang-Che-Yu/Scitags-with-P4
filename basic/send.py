import socket
import time

client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
client_socket.connect(('bbff::22', 12345))

while True:
    data = 'Message'
    client_socket.send(data.encode())
    print(data)
    time.sleep(2)

