#!/bin/bash

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

# Get the number of CPU cores and CPU mask for dynamic configuration
CPU_CORES=$(nproc)
CPU_MASK=$(printf '%x' $((2**CPU_CORES - 1))) # Hex mask for all available cores
echo "Detected $CPU_CORES CPU cores. Using CPU mask: $CPU_MASK for IRQ and RPS/RFS settings."

# Parse input arguments to determine steps to run
steps_to_run=()
if [[ $# -eq 0 ]]; then
    # No arguments passed, run all steps
    steps_to_run=(1 2 3 4 5)
elif [[ $1 =~ ^-([0-9]+)$ ]]; then
    # Range specified, e.g., -5 for steps 1 to 5
    for i in $(seq 1 ${BASH_REMATCH[1]}); do
        steps_to_run+=($i)
    done
else
    # Individual steps specified
    steps_to_run=("$@")
fi

# Step 1: Increase max file descriptors
if [[ " ${steps_to_run[@]} " =~ " 1 " ]]; then
    echo "Step 1: Increasing the maximum number of open file descriptors..."
    ulimit -n 100000
    echo "Max file descriptors increased to 100000."
fi

# Step 2: Configure IRQ affinity for network interfaces
if [[ " ${steps_to_run[@]} " =~ " 2 " ]]; then
    echo "Step 2: Configuring IRQ affinity for network interfaces..."
    for dev in $(ls /sys/class/net/ | grep -v lo); do
        echo "Applying IRQ affinity for device: $dev"
        for irq in $(grep $dev /proc/interrupts | cut -d':' -f1 | tr -d ' '); do
            echo "$CPU_MASK" > /proc/irq/$irq/smp_affinity
            echo "Set IRQ $irq affinity to CPU mask $CPU_MASK."
        done
    done
fi

# Step 3: Configure RPS (Receive Packet Steering) and RFS (Receive Flow Steering)
if [[ " ${steps_to_run[@]} " =~ " 3 " ]]; then
    echo "Step 3: Configuring RPS and RFS settings..."
    sysctl -w net.core.rps_sock_flow_entries=32768
    for dev in $(ls /sys/class/net/ | grep -v lo); do
        RX_QUEUES=$(ls -1 /sys/class/net/$dev/queues/ | grep rx- | wc -l)
        rps_flow_cnt=$((32768 / RX_QUEUES))
        for queue in /sys/class/net/$dev/queues/rx-*; do
            echo "$CPU_MASK" > "$queue/rps_cpus"
            echo "$rps_flow_cnt" > "$queue/rps_flow_cnt"
            echo "Set RPS and RFS for $queue with CPU mask $CPU_MASK and flow count $rps_flow_cnt."
        done
    done
fi

# Step 4: Enable RSS (Receive-Side Scaling) if supported by NIC
if [[ " ${steps_to_run[@]} " =~ " 4 " ]]; then
    echo "Step 4: Enabling RSS if supported by NIC..."
    for dev in $(ls /sys/class/net/ | grep -v lo); do
        if [ -d "/sys/class/net/$dev/queues/rx-queue" ]; then
            echo "Setting RSS for $dev..."
            for queue in /sys/class/net/$dev/queues/rx-*; do
                echo "$CPU_MASK" > "$queue/rps_cpus"
                echo "Set RSS for $queue with CPU mask $CPU_MASK."
            done
        fi
    done
fi

# Step 5: Enable and restart irqbalance service
if [[ " ${steps_to_run[@]} " =~ " 5 " ]]; then
    echo "Step 5: Enabling and restarting irqbalance service..."
    systemctl enable irqbalance
    systemctl restart irqbalance
    echo "irqbalance service restarted and enabled."
fi

# Confirmation of completion
echo "Selected steps have been completed."
