"""
LAB17 - Final FTP-like TCP Server
Port: 9092
Purpose: safe educational file server with authentication, threading, logging,
and protected workspace paths.

Important: This is not real FTP. It is a learning protocol built on TCP sockets.
"""
import logging
import socket
import threading
from pathlib import Path

HOST = "0.0.0.0"
PORT = 9092

BASE_DIR = Path(__file__).resolve().parent
WORKSPACE = BASE_DIR / "server_workspace" / "public"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "server.log"

USERNAME = "student"
PASSWORD = "lab17"

WORKSPACE.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def safe_path(user_path: str = "") -> Path:
    """Resolve a user path and prevent access outside WORKSPACE."""
    clean_path = (user_path or "").strip().lstrip("/")
    candidate = (WORKSPACE / clean_path).resolve()
    workspace_root = WORKSPACE.resolve()

    if candidate != workspace_root and workspace_root not in candidate.parents:
        raise ValueError("forbidden path outside workspace")

    return candidate


def require_auth(args: list[str]) -> tuple[bool, str]:
    if len(args) < 2:
        return False, "ERROR authentication required: <username> <password>"
    if args[0] != USERNAME or args[1] != PASSWORD:
        return False, "ERROR invalid username or password"
    return True, "OK authenticated"


def help_text() -> str:
    return (
        "OK Available commands:\n"
        "  help\n"
        "  login <username> <password>\n"
        "  pwd <username> <password>\n"
        "  ls <username> <password> [path]\n"
        "  mkdir <username> <password> <folder>\n"
        "  rmdir <username> <password> <folder>\n"
        "  rm <username> <password> <file>\n"
        "  rename <username> <password> <old> <new>\n"
        "  upload <username> <password> <file> <content>\n"
        "  download <username> <password> <file>\n"
        "  cat <username> <password> <file>\n"
        "  quit\n"
    )


def process(request: str, client_ip: str = "unknown") -> str:
    request = request.strip()
    if not request:
        return "ERROR empty request"

    parts = request.split(" ", 3)
    command = parts[0].lower()
    args = parts[1:]

    logging.info("client=%s request=%s", client_ip, request)

    if command == "help":
        return help_text()

    if command == "quit":
        return "OK goodbye"

    if command == "login":
        ok, message = require_auth(args)
        return "OK login successful" if ok else message

    ok, message = require_auth(args)
    if not ok:
        return message

    # After username and password, the rest is the real command argument string.
    real = args[2] if len(args) > 2 else ""

    try:
        if command == "pwd":
            return "OK /"

        if command == "ls":
            target = safe_path(real)
            if not target.exists():
                return "ERROR path does not exist"
            if not target.is_dir():
                return "ERROR path is not a directory"
            items = [item.name + ("/" if item.is_dir() else "") for item in sorted(target.iterdir())]
            return "OK " + ("\n".join(items) if items else "empty directory")

        if command == "mkdir":
            if not real:
                return "ERROR usage: mkdir <username> <password> <folder>"
            safe_path(real).mkdir(parents=True, exist_ok=True)
            return f"OK folder created: {real}"

        if command == "rmdir":
            if not real:
                return "ERROR usage: rmdir <username> <password> <folder>"
            target = safe_path(real)
            if not target.exists():
                return "ERROR folder does not exist"
            if not target.is_dir():
                return "ERROR target is not a folder"
            target.rmdir()
            return f"OK folder removed: {real}"

        if command == "rm":
            if not real:
                return "ERROR usage: rm <username> <password> <file>"
            target = safe_path(real)
            if not target.exists():
                return "ERROR file does not exist"
            if not target.is_file():
                return "ERROR target is not a file"
            target.unlink()
            return f"OK file removed: {real}"

        if command == "rename":
            rename_parts = real.split(" ", 1)
            if len(rename_parts) != 2:
                return "ERROR usage: rename <username> <password> <old> <new>"
            old_path = safe_path(rename_parts[0])
            new_path = safe_path(rename_parts[1])
            if not old_path.exists():
                return "ERROR old path does not exist"
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)
            return f"OK renamed {rename_parts[0]} to {rename_parts[1]}"

        if command == "upload":
            upload_parts = real.split(" ", 1)
            if len(upload_parts) != 2:
                return "ERROR usage: upload <username> <password> <file> <content>"
            filename, content = upload_parts
            target = safe_path(filename)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"OK uploaded: {filename}"

        if command in {"download", "cat"}:
            if not real:
                return f"ERROR usage: {command} <username> <password> <file>"
            target = safe_path(real)
            if not target.exists():
                return "ERROR file does not exist"
            if not target.is_file():
                return "ERROR target is not a file"
            return "OK\n" + target.read_text(encoding="utf-8", errors="replace")

        return "ERROR unknown command"

    except ValueError as exc:
        logging.warning("security warning client=%s error=%s", client_ip, exc)
        return f"ERROR {exc}"
    except OSError as exc:
        logging.error("os error client=%s error=%s", client_ip, exc)
        return f"ERROR operating system error: {exc}"
    except Exception as exc:
        logging.exception("unexpected error client=%s", client_ip)
        return f"ERROR unexpected server error: {exc}"


def handle_client(conn: socket.socket, addr) -> None:
    client_ip = addr[0]
    with conn:
        data = conn.recv(65536)
        if not data:
            conn.sendall(b"ERROR empty request")
            return
        response = process(data.decode("utf-8", errors="replace"), client_ip)
        conn.sendall(response.encode("utf-8"))


def main() -> None:
    print(f"Final FTP-like server is listening on {HOST}:{PORT}")
    print(f"Workspace: {WORKSPACE}")
    print(f"Log file: {LOG_FILE}")
    print(f"Default credentials: {USERNAME} / {PASSWORD}")
    print("Press Ctrl+C to stop.")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(20)

        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
