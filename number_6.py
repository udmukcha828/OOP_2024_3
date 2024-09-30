import os
import threading
import queue
import time
import re

# Compile regex to find out how many packages were received
received_packages = re.compile(r"(\d+) received")
status = ("no response", "alive but losses", "alive")

def check_address(ip_queue, result_queue):
    """Check availability of an IP address using PING command."""
    while True:
        if not ip_queue.empty():
            ip = ip_queue.get()
            print(f"... pinging {ip}")
            ping_out = os.popen(f"ping -q -c2 {ip}", "r")
            while True:
                line = ping_out.readline().strip()
                if not line:
                    break
                match = received_packages.search(line)
                if match:
                    count = int(match.group(1))
                    result_queue.put((ip, status[count]))
                    break
            ping_out.close()

# Initialize queues
ip_queue = queue.Queue()
result_queue = queue.Queue()

# Add IP addresses to be checked
ips = ["192.168.178." + str(x) for x in range(20, 30)]
for ip in ips:
    ip_queue.put(ip)

# Start worker threads
num_workers = len(ips)
worker_threads = []
for _ in range(num_workers):
    t = threading.Thread(target=check_address, args=(ip_queue, result_queue))
    t.daemon = True
    t.start()
    worker_threads.append(t)

# Wait for all results
results = []
while len(results) < num_workers:
    ip, status = result_queue.get()
    results.append((ip, status))

# Print results
for ip, status in sorted(results):
    print(f"{ip}: {status}")

# Join all worker threads
for t in worker_threads:
    t.join()
