import socket
host = "db.wxrwmfhnbgbbqcoqfcba.supabase.co"
try:
    print(f"Resolving {host} with getaddrinfo...")
    results = socket.getaddrinfo(host, 5432)
    for res in results:
        print(f"Result: {res}")
except Exception as e:
    print(f"Error: {e}")
