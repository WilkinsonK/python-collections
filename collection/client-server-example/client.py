import socket

HOST = "127.0.0.1"
PORT = 47716

to_send = input("send to server: ")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(bytes(to_send, encoding="utf-8"))

    data = sock.recv(1024)

print(f"received from server: {data!r}")
