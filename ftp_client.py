"""Minimal one-command client for LAB17."""
import socket
import sys

HOST = "127.0.0.1"
PORT = 9092

if len(sys.argv) < 2:
    print('Usage: python3 ftp_client.py "help"')
    raise SystemExit(1)

command = " ".join(sys.argv[1:])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    sock.sendall(command.encode("utf-8"))
    print(sock.recv(65536).decode("utf-8", errors="replace"))
