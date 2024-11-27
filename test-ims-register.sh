#!/bin/bash

# Check if the user provided an argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <count>"
    exit 1
fi

# Read the call number from the command-line argument
n=$1

# source config
# Define cleanup function to stop all local and remote processes
cleanup() {
    echo "Stopping tcpdump, pidstat, and remote SSH commands..."
    kill $TCPDUMP_PID 2>/dev/null
    wait $TCPDUMP_PID 2>/dev/null
    echo "All processes stopped."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Start tcpdump in the background, saving to ${n}test.pcap, and save its PID
tcpdump -i any -w "${n}test.pcap" &
TCPDUMP_PID=$!

SIPP_CLIENT_CMD = "./sipp -sf register.xml -inf users.csv 172.16.100.74 -m ${n}"
SIPP_CLIENT_DIR="/root/sipp"
# Run the second SSH command and capture its output
cd ${SIPP_CLIENT_DIR} && ${SIPP_CLIENT_CMD} > "${n}_sipp_client.log" 
echo "Main remote command completed."

# After the main SSH command completes, stop tcpdump, pidstat, and the watcher
cleanup

# Notify the user where logs are saved
echo "SIPp client and server logs saved as:"
echo "  - ${n}_sipp_client.log"

./parse_sipp_output ${n}_sipp_client.log


# # Run the rtp_analyse Python file, redirecting output to "${n}test.txt"
# echo "Running rtp-analyse.py with ${n}test.pcap, outputting to ${n}test.txt..."
# python3 ./rtp-analyse.py "${n}test.pcap" > "${n}test.txt"
# if [ $? -ne 0 ]; then
#   echo "Error: rtp-analyse.py failed."
#   exit 1
# fi
# echo "Successfully ran rtp-analyse.py, output saved to ${n}test.txt."

# # Remove the file "${n}test.pcap"
# echo "Removing ${n}test.pcap..."
# rm "${n}test.pcap"
# if [ $? -ne 0 ]; then
#   echo "Error: failed to remove ${n}test.pcap."
#   exit 1
# fi
# echo "Successfully removed ${n}test.pcap."

# cat "${n}test.txt"

# TODO: rtpengine log analysis