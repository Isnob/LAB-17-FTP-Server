"""
LAB17 - Smart FTP-like Client
Connects to the final server on port 9092.
After login, students may type short commands without repeating credentials.
"""
import socket
from pathlib import Path

HOST = "127.0.0.1"  # Change to 192.168.56.101 when testing from Linux Mint VM.
PORT = 9092
DEFAULT_USERNAME = "student"
DEFAULT_PASSWORD = "lab17"
DOWNLOAD_DIR = Path("client_downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

AUTH_COMMANDS = {"pwd", "ls", "mkdir", "rmdir", "rm", "rename", "upload", "download", "cat"}


def send_command(command: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        sock.sendall(command.encode("utf-8"))
        return sock.recv(65536).decode("utf-8", errors="replace")


def add_credentials(command: str, username: str, password: str) -> str:
    parts = command.split(" ", 1)
    action = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    if action not in AUTH_COMMANDS:
        return command

    # Do not duplicate credentials if the full command is already written.
    rest_parts = rest.split(" ", 2)
    if len(rest_parts) >= 2 and rest_parts[0] == username and rest_parts[1] == password:
        return command

    return f"{action} {username} {password}" + (f" {rest}" if rest else "")


def main() -> None:
    username = DEFAULT_USERNAME
    password = DEFAULT_PASSWORD

    print("Smart FTP-like Client")
    print(f"Server: {HOST}:{PORT}")
    print("Default login: student / lab17")
    print("First type: login student lab17")
    print("Then type short commands: mkdir docs | upload docs/note.txt Hello | ls docs | cat docs/note.txt")
    print("Local save command: save <server_file> <local_file>")
    print("Type quit to close the client.\n")

    while True:
        try:
            command = input("myftp@shell$ ").strip()
        except KeyboardInterrupt:
            print("\nClient closed.")
            break

        if not command:
            continue

        if command == "quit":
            print(send_command("quit"))
            print("Client closed.")
            break

        if command.startswith("login "):
            pieces = command.split(" ", 2)
            if len(pieces) == 3:
                username, password = pieces[1], pieces[2]
            print(send_command(command))
            continue

        if command.startswith("save "):
            pieces = command.split(" ", 2)
            if len(pieces) != 3:
                print("ERROR usage: save <server_file> <local_file>")
                continue
            response = send_command(f"download {username} {password} {pieces[1]}")
            if response.startswith("OK\n"):
                target = DOWNLOAD_DIR / pieces[2]
                target.write_text(response[3:], encoding="utf-8")
                print(f"OK saved to {target}")
            else:
                print(response)
            continue

        try:
            print(send_command(add_credentials(command, username, password)))
        except ConnectionRefusedError:
            print("ERROR server is not running or wrong HOST/PORT")
        except Exception as exc:
            print(f"ERROR {exc}")


if __name__ == "__main__":
    main()
