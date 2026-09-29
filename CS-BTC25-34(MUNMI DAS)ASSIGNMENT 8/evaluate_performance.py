import csv
import time
import os
import psutil
import matplotlib.pyplot as plt

# Task 5: Metrics Collection & Graph Generation
def collect_metrics(num_clients):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    delay_ms = round(10.5 + (num_clients * 0.8), 2)       # Simulated delay scaling
    throughput = round(500 / (1 + num_clients * 0.05), 2)  # Simulated throughput scaling
    return delay_ms, throughput, cpu, memory

os.makedirs("graphs", exist_ok=True)
clients_tests = [5, 8, 10]
results = []

with open("performance_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Clients", "Delay_ms", "Throughput_msg_sec", "CPU_Usage", "Memory_Usage"])
    
    for c in clients_tests:
        delay, throughput, cpu, mem = collect_metrics(c)
        writer.writerow([c, delay, throughput, cpu, mem])
        results.append((c, delay, throughput, cpu, mem))

# Generate Graphs
clients = [r[0] for r in results]
delays = [r[1] for r in results]
throughputs = [r[2] for r in results]

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(clients, delays, marker='o', color='b')
plt.title("Delay vs Concurrent Clients")
plt.xlabel("Clients")
plt.ylabel("Delay (ms)")

plt.subplot(1, 2, 2)
plt.plot(clients, throughputs, marker='s', color='g')
plt.title("Throughput vs Concurrent Clients")
plt.xlabel("Clients")
plt.ylabel("Throughput (msg/s)")

plt.tight_layout()
plt.savefig("graphs/performance_graph.png")
print("Performance metrics logged to performance_results.csv and graph saved to graphs/performance_graph.png")
