#!/bin/bash

# Function to run a command as a daemon on a remote machine using SSH and password
run_remote_daemon() {
    local command="$1"
    local remote="$2"
    local password="$3"
    local working_directory="$4"
    
    sshpass -p "$password" ssh "$remote" "cd $working_directory && nohup $command &"
    echo "Daemon process started with SSH command on $remote"
}

# Function to run a local daemon and capture output
run_daemon() {
    local command="$1"
    local working_directory="$2"
    local log_file="$3"
    
    cd "$working_directory"
    if [ -n "$log_file" ]; then
        nohup $command > "$log_file" 2>&1 &
    else
        nohup $command &
    fi
    echo "Daemon process '$command' executed in directory $working_directory"
}

# Function to kill processes by PID or name
kill_process() {
    local target="$1"
    if [[ "$target" =~ ^[0-9]+$ ]]; then
        kill -9 "$target"
        echo "Killed process with PID: $target"
    else
        pkill -9 -f "$target"
        echo "Killed processes by name: $target"
    fi
}

# Function to monitor rtpengine log file
check_rtpengine_log() {
    local log_file="$1"
    tail -F "$log_file" | while read line; do
        echo -e "\n\ntest is failed and aborted: $line"
        kill_process "kamailio"
        kill_process "rtpengine"
        kill_process "tcpdump"
        kill_process "pidstat"
        exit 1
    done
}

# Function to read configuration from a file
read_config() {
    local file_path="$1"
    declare -A config
    while IFS='=' read -r key value; do
        if [[ ! $key =~ ^# ]]; then
            config[$key]=$value
        fi
    done < "$file_path"
    echo "${config[@]}"
}

# Main script execution
project_dir="$(pwd)"
config_file="${project_dir}/config"
config=$(read_config "$config_file")
log_file_path="${config[RTPENGINE_DIR]}/rtpengine.log"

if [ "$#" -lt 1 ]; then
    echo "Input call count"
    exit 1
fi
test_id="$1"

# Start a background log monitor
check_rtpengine_log "$log_file_path" &

# Get rtpengine PID
rtpengine_pid=$(pidof rtpengine)
if [ -z "$rtpengine_pid" ]; then
    echo "RTPengine PID not found. Unable to start the test."
    exit 0
fi

# Start pidstat process
pidstat_command="pidstat -p $rtpengine_pid 1"
pidstat_log_file="${project_dir}/test${test_id}.log"
run_daemon "$pidstat_command" "$project_dir" "$pidstat_log_file"
sleep 3

echo "Testing on n=$test_id"

# Start tcpdump process
tcpdump_log_file="test${test_id}.pcap"
tcpdump_command="tcpdump -i ens192 -w $tcpdump_log_file"
run_daemon "$tcpdump_command" "$project_dir"
sleep 3

# Run remote server command
server_command="${config[SIPP_SERVER_CMD]} $test_id"
run_remote_daemon "$server_command" "${config[SIPP_SERVER_USER]}@${config[SIPP_SERVER]}" "${config[SIPP_SERVER_PASSWORD]}" "${config[SIPP_SERVER_DIR]}"
sleep 3

# Run remote client command
client_command="${config[SIPP_CLIENT_CMD]} $test_id"
run_remote_daemon "$client_command" "${config[SIPP_CLIENT_USER]}@${config[SIPP_CLIENT]}" "${config[SIPP_CLIENT_PASSWORD]}" "${config[SIPP_CLIENT_DIR]}"
sleep 3

# Wait for client process to finish
wait $!
echo "Stopping pidstat... Logs saved in $pidstat_log_file"
kill_process "$rtpengine_pid"
sleep 3

echo "Stopping tcpdump... Saved in $tcpdump_log_file"
kill_process "tcpdump"
sleep 3
