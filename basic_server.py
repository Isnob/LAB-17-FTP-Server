"""
LAB17 - Basic TCP File Server
Port: 9090
Purpose: first step for beginners. It accepts one command per TCP connection.
"""
import os
import socket

HOST = "0.0.0.0"
PORT = 9090
WORKSPACE = "server_workspace/public"

os.makedirs(WORKSPACE, exist_ok=True)


def process(request: str) -> str:
    """Process a small set of commands without authentication."""
    request = request.strip()

    if not request:
        return "ERROR empty request"

    if request == "help":
        return "OK commands: help, pwd, ls, mkdir <folder>, quit"

    if request == "quit":
        return "OK goodbye"

    if request == "pwd":
        return "OK /"

    if request == "ls":
        items = os.listdir(WORKSPACE)
        return "OK " + ("\n".join(items) if items else "empty directory")

    if request.startswith("mkdir "):
        folder_name = request.split(" ", 1)[1].strip()
        if not folder_name:
            return "ERROR folder name is required"
        path = os.path.join(WORKSPACE, folder_name)
        os.makedirs(path, exist_ok=True)
        return f"OK folder created: {folder_name}"

    return "ERROR unknown command"


def main() -> None:
    print(f"Basic server is listening on {HOST}:{PORT}")
    print(f"Workspace: {WORKSPACE}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(5)

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Client connected: {addr}")
                data = conn.recv(4096)
                if not data:
                    conn.sendall(b"ERROR empty request")
                    continue
                response = process(data.decode("utf-8", errors="replace"))
                conn.sendall(response.encode("utf-8"))


if __name__ == "__main__":
    main()
