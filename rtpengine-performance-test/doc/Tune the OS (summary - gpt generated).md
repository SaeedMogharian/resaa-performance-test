https://github.com/sorooshm78/system-telephony?tab=readme-ov-file#linux

This content covers how Linux manages interrupts and optimizes network packet processing across multiple CPUs, including the use of tools like `ethtool`, RPS, RFS, and RSS. Here’s a breakdown of the key points:

1. **Interrupts and CPU Affinity**:
   - **Interrupts** allow hardware to notify the CPU of events, prompting it to handle data from devices like Network Interface Cards (NICs).
   - **SMP IRQ Affinity**: You can assign interrupts from NICs to specific CPUs, helping prevent CPU overload. Without SMP IRQ affinity, all NIC interrupts go to CPU 0, potentially creating bottlenecks.
   
2. **Receive Packet Steering (RPS)**:
   - **RPS** distributes network packets to different CPUs by calculating a hash from packet data, ensuring network processing uses multiple CPUs effectively.
   - It’s software-based, ideal for single-queue NICs, but can cause CPU cache issues when different CPUs handle interrupts and applications simultaneously.

3. **Receive Flow Steering (RFS)**:
   - **RFS** improves on RPS by ensuring the same CPU handles both the network interrupt and the application consuming the packet, enhancing cache usage efficiency and reducing latency.
   
4. **Receive-Side Scaling (RSS)**:
   - **RSS** utilizes multiple hardware queues in a NIC, distributing interrupt processing across CPUs to balance load and reduce latency.

5. **Configuring RPS and RFS**:
   - **RPS** and **RFS** settings involve files like `/sys/class/net/device/queues/rx-queue/rps_cpus` and `/proc/sys/net/core/rps_sock_flow_entries`.
   - **CPU Affinity and Bitmasking**: Use bitmask values to assign specific CPUs, with tools like the CPU affinity calculator for precision.

6. **NIC Offloads**:
   - Offload features like **TCP Segmentation Offload (TSO)** and **Generic Receive Offload (GRO)** allow the NIC to handle certain network tasks instead of the CPU, enhancing throughput.

7. **Using `ethtool`**:
   - The **`ethtool`** command manages NIC settings such as interrupt coalescing, packet steering, and offload settings, making it essential for network performance tuning.

8. **Syslog Logging Driver**:
   - Docker log drivers manage container logs, directing them to locations like syslog, journald, or third-party collectors (Fluentd), with configuration flexibility for each driver.

In summary, Linux’s advanced interrupt and network steering features—alongside tools like `ethtool` and Docker logging options—allow for efficient network performance management. This setup supports high network loads while balancing CPU utilization across available cores.

