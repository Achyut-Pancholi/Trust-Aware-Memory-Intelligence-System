import os
import subprocess
import sys
import socket
import time

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def ensure_backend_running():
    try:
        if not is_port_in_use(8000):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            if os.path.basename(current_dir) == 'pages':
                root_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
            else:
                root_dir = os.path.abspath(os.path.join(current_dir, '..'))
                
            log_path = os.path.join(root_dir, "backend_server.log")
            log_file = open(log_path, "w")
            subprocess.Popen([
                sys.executable, "-m", "uvicorn", "backend.main:app", 
                "--host", "0.0.0.0", "--port", "8000"
            ], cwd=root_dir, stdout=log_file, stderr=subprocess.STDOUT)
            time.sleep(4) # Give it a few seconds to boot up
    except Exception as e:
        print("Failed to start backend subprocess:", e)
