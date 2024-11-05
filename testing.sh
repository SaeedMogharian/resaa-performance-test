#!/bin/bash

# Get a number input from the user
read -p "Enter the call number: " n

source config

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
    sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no ${SIPP_CLIENT_USER}@${SIPP_CLIENT} "pkill -f run_background_task.sh; pkill -f run_performance_test./sh" 2>/dev/null
    wait $TCPDUMP_PID $PIDSTAT_PID $WATCH_PID 2>/dev/null
    echo "All processes stopped."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT


# Start tcpdump in the background, saving to ${n}test.pcap, and save its PID
tcpdump -i any -w "${n}test.pcap" &
TCPDUMP_PID=$!

# Start pidstat for rtpengine PID in the background, outputting to ${n}test.log
pidstat -p $RTPENGINE_PID 1 > "${n}test.log" &
PIDSTAT_PID=$!

# Run the first SSH command in the background
echo "Starting first remote command on ${SIPP_SERVER} in the background..."
sshpass -p "${SIPP_SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SIPP_SERVER_USER}@${SIPP_SERVER} "cd ${SIPP_SERVER_DIR} && ulimit -n 10000 && ${SIPP_SERVER_CMD} ${n}" &
BACKGROUND_SSH_PID=$!

# Run the second SSH command and wait for it to complete
echo "Starting main remote command on ${SIPP_CLIENT}..."
sshpass -p "${SIPP_CLIENT_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SIPP_CLIENT_USER}@${SIPP_CLIENT} "cd ${SIPP_CLIENT_DIR} && ulimit -n 10000 && ${SIPP_CLIENT_CMD} ${n}"
echo "Main remote command completed."

# After the main SSH command completes, stop tcpdump, pidstat, and the watcher
cleanup

# Run the rtp_analyse Python file, redirecting output to "${n}test.txt"
echo "Running rtp-analyse.py with ${n}test.pcap, outputting to ${n}test.txt..."
python3 ./rtp-analyse.py "${n}test.pcap" > "${n}test.txt"
if [ $? -ne 0 ]; then
  echo "Error: rtp-analyse.py failed."
  exit 1
fi
echo "Successfully ran rtp-analyse.py, output saved to ${n}test.txt."

# Remove the file "${n}test.pcap"
echo "Removing ${n}test.pcap..."
rm "${n}test.pcap"
if [ $? -ne 0 ]; then
  echo "Error: failed to remove ${n}test.pcap."
  exit 1
fi
echo "Successfully removed ${n}test.pcap."

cat "${n}test.txt"

# TODO: rtpengine log analysis