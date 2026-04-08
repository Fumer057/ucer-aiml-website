import socket
try:
    print(f"Resolving google.com...")
    print(f"IP: {socket.gethostbyname('google.com')}")
except Exception as e:
    print(f"Error: {e}")
