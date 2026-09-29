import matplotlib.pyplot as plt
import pandas as pd
import os

# Create directory for graphs
os.makedirs("graphs", exist_ok=True)

# Load CSV data
df = pd.read_csv("performance_results.csv")

# Create plot layout (1 row, 2 columns)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Delay vs Concurrent Clients
ax1.plot(df['Clients'], df['Delay_ms'], marker='o', color='crimson', linewidth=2)
ax1.set_title('Delay vs Concurrent Clients')
ax1.set_xlabel('Clients')
ax1.set_ylabel('Delay (ms)')
ax1.grid(True, linestyle='--')

# Plot 2: Throughput vs Concurrent Clients
ax2.plot(df['Clients'], df['Throughput_msg_sec'], marker='s', color='teal', linewidth=2)
ax2.set_title('Throughput vs Concurrent Clients')
ax2.set_xlabel('Clients')
ax2.set_ylabel('Throughput (msg/sec)')
ax2.grid(True, linestyle='--')

# Save image in graphs folder
plt.tight_layout()
plt.savefig("graphs/performance_graph.png", dpi=300)
print("Graph saved successfully under graphs/performance_graph.png")
