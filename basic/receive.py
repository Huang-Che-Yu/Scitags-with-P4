import socket

server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
server_socket.bind(('bbff::11', 12345))
server_socket.listen(5)

print("Server listening on port 12345...")
conn, addr = server_socket.accept()
print(f"Connection established with {addr}")

while True:
    conn, addr = server_socket.accept()
    print(f"Connection established with {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            break
        print(f"Received: {data.decode()}")
    conn.close()
    print("Connection close")
