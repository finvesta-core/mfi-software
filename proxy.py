# proxy.py
import os
import threading
import time
from pgsqlite import Proxy

POSTGRES_URL = os.environ.get('DATABASE_URL')

if not POSTGRES_URL:
    print("ERROR: DATABASE_URL not set!")
    exit(1)

print(f"Starting pgsqlite proxy → {POSTGRES_URL}")

def run_proxy():
    proxy = Proxy(POSTGRES_URL, port=5433)
    proxy.run()

thread = threading.Thread(target=run_proxy, daemon=True)
thread.start()

# Wait for proxy to start
time.sleep(3)
print("Proxy ready at http://localhost:5433")