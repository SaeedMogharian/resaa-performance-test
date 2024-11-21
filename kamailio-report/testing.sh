#!/bin/bash

# Get a number input from the user
read -p "Enter test start rate: " n

source config


SIPP_SERVER_CMD="./sipp -sf server.xml $MACHINE_IP -m ${n*$INTERVAL_TIME}"
SIPP_CLIENT_CMD=


# Find the PID of the kamailio process
KAMAILIO_PID=$(pidstat | grep kamailio | awk '{print $4}')

# Check if kamailio PID is found
if [[ -z "$KAMAILIO_PID" ]]; then
    echo "Error: kamailio process not found."
    exit 1
fi

# Define cleanup function to stop all local and remote processes
cleanup() {
    echo "Stopping tcpdump, pidstat, and remote SSH commands..."
    # sshpass -p "$ssh_password" ssh -o StrictHostKeyChecking=no ${SIPP_CLIENT_USER}@${SIPP_CLIENT} "pkill -f run_background_task.sh; pkill -f run_performance_test./sh" 2>/dev/null
    wait $TCPDUMP_PID $PIDSTAT_PID $WATCH_PID 2>/dev/null
    echo "All processes stopped."
}

# Trap SIGINT (Ctrl+C) and call cleanup
trap cleanup SIGINT

# Start pidstat for kamailio PID in the background, outputting to ${n}test.log
pidstat -p $KAMAILIO_PID 1 > "${n}test.log" &
PIDSTAT_PID=$!

# Run the first SSH command in the background
echo "Starting first remote command on ${SIPP_SERVER} in the background..."
sshpass -p "${SIPP_SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SIPP_SERVER_USER}@${SIPP_SERVER} "cd ${SIPP_SERVER_DIR} && ulimit -n 10000 && ${SIPP_SERVER_CMD} ${n}" &
BACKGROUND_SSH_PID=$!

# Run the second SSH command and wait for it to complete
echo "Starting main remote command on ${SIPP_CLIENT}..."
sshpass -p "${SIPP_CLIENT_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SIPP_CLIENT_USER}@${SIPP_CLIENT} "cd ${SIPP_CLIENT_DIR} && ulimit -n 10000 && ${SIPP_CLIENT_CMD} ${n}" > sipp_output.log
echo "Main remote command completed."

# After the main SSH command completes, stop tcpdump, pidstat, and the watcher
cleanup

# Function to calculate fail rate on client side
calculate_fail_rate() {
    OUTPUT_FILE="sipp_output.log"

    # Read the SIPp output file
    if [[ -f "$OUTPUT_FILE" ]]; then
        successful_calls=$(grep -oP "Successful call\s+\|\s+[^\|]+\|\s+\K\d+" "$OUTPUT_FILE" | tail -1)
        failed_calls=$(grep -oP "Failed call\s+\|\s+[^\|]+\|\s+\K\d+" "$OUTPUT_FILE" | tail -1)

        # Convert to integers or set to zero if no match found
        successful_calls=${successful_calls:-0}
        failed_calls=${failed_calls:-0}

        # Calculate total calls and failed call rate
        total_calls=$((successful_calls + failed_calls))
        if (( total_calls > 0 )); then
            failed_call_rate=$(awk "BEGIN {printf \"%.2f\", ($failed_calls / $total_calls) * 100}")
        else
            failed_call_rate=0
        fi

        echo "Total Calls: $total_calls"
        echo "Failed Call Rate: $failed_call_rate%"
    else
        echo "Error: SIPp output file not found."
    fi
}

# Call the function to calculate and display the fail rate
calculate_fail_rate()
