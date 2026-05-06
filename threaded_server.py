"""
LAB17 - Threaded TCP File Server
Port: 9091
Purpose: show how one server can handle many clients using threading.
"""
import os
import socket
import threading

HOST = "0.0.0.0"
PORT = 9091
WORKSPACE = "server_workspace/public"

os.makedirs(WORKSPACE, exist_ok=True)


def process(request: str) -> str:
    request = request.strip()

    if not request:
        return "ERROR empty request"

    if request == "help":
        return "OK commands: help, pwd, ls, mkdir <folder>, upload <file> <content>, cat <file>, quit"

    if request == "quit":
        return "OK goodbye"

    if request == "pwd":
        return "OK /"

    if request == "ls":
        items = os.listdir(WORKSPACE)
        return "OK " + ("\n".join(items) if items else "empty directory")

    if request.startswith("mkdir "):
        folder_name = request.split(" ", 1)[1].strip()
        os.makedirs(os.path.join(WORKSPACE, folder_name), exist_ok=True)
        return f"OK folder created: {folder_name}"

    if request.startswith("upload "):
        parts = request.split(" ", 2)
        if len(parts) < 3:
            return "ERROR usage: upload <file> <content>"
        filename, content = parts[1], parts[2]
        with open(os.path.join(WORKSPACE, filename), "w", encoding="utf-8") as file:
            file.write(content)
        return f"OK uploaded: {filename}"

    if request.startswith("cat "):
        filename = request.split(" ", 1)[1].strip()
        path = os.path.join(WORKSPACE, filename)
        if not os.path.isfile(path):
            return "ERROR file does not exist"
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            return "OK\n" + file.read()

    return "ERROR unknown command"


def handle_client(conn: socket.socket, addr) -> None:
    with conn:
        print(f"Thread {threading.current_thread().name} handles {addr}")
        data = conn.recv(8192)
        if not data:
            conn.sendall(b"ERROR empty request")
            return
        response = process(data.decode("utf-8", errors="replace"))
        conn.sendall(response.encode("utf-8"))


def main() -> None:
    print(f"Threaded server is listening on {HOST}:{PORT}")
    print(f"Workspace: {WORKSPACE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(20)

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()


if __name__ == "__main__":
    main()
