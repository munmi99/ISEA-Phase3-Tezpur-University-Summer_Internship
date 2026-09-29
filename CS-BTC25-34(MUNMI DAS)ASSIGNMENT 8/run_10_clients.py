import subprocess
import time

processes = []
print("Starting 10 concurrent clients...")

# Spawns 10 client processes automatically
for i in range(10):
    p = subprocess.Popen(["python3", "client_gui.py"])
    processes.append(p)
    time.sleep(0.2) # Chota delay stability ke liye

print("10 clients launched successfully!")
