import requests
import socket


def check_internet():
    try:
        requests.get(
            "https://www.google.com",
            timeout=3,
        )
        return True

    except Exception:
        return False


def check_bbg_connection():
    try:
        socket.create_connection(
            ("localhost", 8194),
            timeout=3,
        )
        return True

    except OSError:
        return False
