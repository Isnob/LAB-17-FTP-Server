"""Simple manual test client for final server on port 9092.

Run the server first in another terminal:
    python3 ftp_server.py

Then run:
    python3 tests/test_client.py
"""
import socket
import sys

HOST = "127.0.0.1"
PORT = 9092

commands = [
    "help",
    "login student lab17",
    "pwd student lab17",
    "mkdir student lab17 docs",
    "upload student lab17 docs/hello.txt Hello from automated test",
    "ls student lab17 docs",
    "cat student lab17 docs/hello.txt",
    "rename student lab17 docs/hello.txt docs/message.txt",
    "download student lab17 docs/message.txt",
    "rm student lab17 docs/message.txt",
    "rmdir student lab17 docs",
    "cat student lab17 ../../etc/passwd",
]


def send(command: str) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(5)
        sock.connect((HOST, PORT))
        sock.sendall(command.encode("utf-8"))
        return sock.recv(65536).decode("utf-8", errors="replace")


def main() -> None:
    print(f"Testing LAB17 FTP-like server on {HOST}:{PORT}")
    print("Make sure ftp_server.py is running in another terminal.\n")

    for command in commands:
        try:
            response = send(command)
        except ConnectionRefusedError:
            print("ERROR: server is not running. Start it first with: python3 ftp_server.py")
            sys.exit(1)
        except socket.timeout:
            print("ERROR: connection timed out. Check HOST, PORT, and firewall settings.")
            sys.exit(1)

        print(f"\n$ {command}\n{response}")

    print("\nAll manual checks finished.")


if __name__ == "__main__":
    main()
