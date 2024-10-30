#!/bin/bash

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Get the number of CPU cores (for use in affinity and RPS/RFS configuration)
CPU_CORES=$(nproc)
CPU_MASK=$(printf '%x' $((2**CPU_CORES - 1))) # Hex mask for all available cores

echo "Detected $CPU_CORES CPU cores. Using CPU mask: $CPU_MASK for IRQ and RPS/RFS settings."

# Increase the maximum number of open file descriptors
echo "Increasing the limit..."
ulimit -n 100000

# Set RPS (Receive Packet Steering) and RFS (Receive Flow Steering) parameters
echo "Configuring RPS and RFS settings and IRQ balancing..."

# Set rps_sock_flow_entries to 32768 for moderate server loads
sysctl -w net.core.rps_sock_flow_entries=32768

# Apply RPS and IRQ affinity settings per network device
for dev in $(ls /sys/class/net/ | grep -v lo); do
    echo "Applying settings for network device: $dev"
    
    # Apply IRQ balancing
    for irq in $(grep $dev /proc/interrupts | cut -d':' -f1 | tr -d ' '); do
        echo "$CPU_MASK" > /proc/irq/$irq/smp_affinity
    done

    # Get the number of RX queues for the device
    RX_QUEUES=$(ls -1 /sys/class/net/$dev/queues/ | grep rx- | wc -l)
    rps_flow_cnt=$((32768 / RX_QUEUES))

    # Configure RPS for each receive queue
    for queue in /sys/class/net/$dev/queues/rx-*; do
        echo "$CPU_MASK" > "$queue/rps_cpus"    # Allow all CPUs to handle RPS for the queue
        echo "$rps_flow_cnt" > "$queue/rps_flow_cnt" # Set flow count for each queue
    done
done

# Enable RSS (Receive-Side Scaling) if supported by NIC
echo "Enabling RSS if supported by NIC..."
for dev in $(ls /sys/class/net/ | grep -v lo); do
    if [ -d "/sys/class/net/$dev/queues/rx-queue" ]; then
        echo "Setting RSS for $dev..."
        for queue in /sys/class/net/$dev/queues/rx-*; do
            echo "$CPU_MASK" > "$queue/rps_cpus" # Apply the CPU mask for RSS
        done
    fi
done

# Restart irqbalance to ensure IRQs are balanced dynamically
echo "Configuring IRQ balancing..."
systemctl enable irqbalance
systemctl restart irqbalance

# Confirm settings
echo "Displaying IRQ and network settings for verification..."
cat /proc/interrupts | grep -E "CPU|eth"
echo "RPS setting for all devices:"
cat /proc/sys/net/core/rps_sock_flow_entries
echo "Done. System tuned dynamically for high network load and IRQ balancing."
