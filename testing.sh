#!/bin/bash

# Get a number input from the user
read -p "Enter a number: " n

# Get the password for SSH
read -sp "Enter SSH password: " ssh_password
echo

# Find the PID of the rtpengine process
RTPENGINE_PID=$(pidstat | grep rtpengine | awk '{print $4}')

# Check if rtpengine PID is found
if [[ -z "$RTPENGINE_PID" ]]; then
    echo "Error: rtpengine process not found."
    exit 1
fi

# Define cleanup function to stop all local and remote processes
cleanup() {
    echo "Stopping tcpdump, pidstat, and remote SSH commands..."
    kill $TCPDUMP_PID $PIDSTAT_PID $WATCH_PID $BACKGROUND_SSH_PID 2>/dev/null
    sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no user@192.168.21.56 "pkill -f run_background_task.sh; pkill -f run_performance_test.sh" 2>/dev/null
    wait $TCPDUMP_PID $PIDSTAT_PID $WATCH_PID 2>/dev/null
    echo "All processes stopped."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

## Watch for changes in /rtpengine/rtpengine.log and abort if any change is detected
#echo "Monitoring /rtpengine/rtpengine.log for changes..."
#tail -F /rtpengine/rtpengine.log | while read -r line; do
#    echo "Change detected in /rtpengine/rtpengine.log: $line"
#    cleanup
#    exit 1
#done &
#
#
#
#
# =$!

# Start tcpdump in the background, saving to test$n.pcap, and save its PID
tcpdump -i any -w "test${n}.pcap" &
TCPDUMP_PID=$!

# Start pidstat for rtpengine PID in the background, outputting to test$n.log
pidstat -p $RTPENGINE_PID 1 > "test${n}.log" &
PIDSTAT_PID=$!

# Run the first SSH command in the background
echo "Starting first remote command on 192.168.21.57 in the background..."
sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no user@192.168.21.57 "cd /root/projects/soroush.m/performance-test/ && ./server-performance.sh ${n}" &
BACKGROUND_SSH_PID=$!

# Run the second SSH command and wait for it to complete
echo "Starting main remote command on 192.168.21.56..."
sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no user@192.168.21.56 "cd /root/projects/soroush.m/performance-test/ && ./client-performance.sh ${n}"
echo "Main remote command completed."

# After the main SSH command completes, stop tcpdump, pidstat, and the watcher
cleanup
