import os
from config import Config

def view_logs():
    log_file = Config.LOG_FILE
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            print(f.read())
    else:
        print("Log file not found.")

if __name__ == "__main__":
    view_logs()
