#!/bin/bash

# Function to parse SIPp output
parse_sipp_output() {
    local output_file="$1"

    if [[ ! -f "$output_file" ]]; then
        echo "Error: File '$output_file' does not exist."
        exit 1
    fi

    # Read data from the file
    local data=$(<"$output_file")

    # Extract Successful Calls
    local successful_calls=$(echo "$data" | grep -oP "Successful call\s+\|\s+[^\|]+\|\s+\K\d+")
    successful_calls=${successful_calls:-0} # Default to 0 if not found

    # Extract Failed Calls
    local failed_calls=$(echo "$data" | grep -oP "Failed call\s+\|\s+[^\|]+\|\s+\K\d+")
    failed_calls=${failed_calls:-0} # Default to 0 if not found

    # Calculate Total Calls
    local total_calls=$((successful_calls + failed_calls))

    # Calculate Failed Call Rate
    local failed_call_rate=0
    if (( total_calls > 0 )); then
        failed_call_rate=$(awk "BEGIN {printf \"%.2f\", ($failed_calls / $total_calls) * 100}")
    fi

    # Extract Call Rate
    local call_rate=$(echo "$data" | grep -oP "Call Rate\s+\|\s+[^\|]+\|\s+\K[\d.]+")
    call_rate=${call_rate:-0.0} # Default to 0.0 if not found

    # Output the results
    echo "Total Calls: $total_calls"
    echo "Failed Call Rate: $failed_call_rate%"
    echo "Successful Calls: $successful_calls"
    echo "Failed Calls: $failed_calls"
    echo "Call Rate: $call_rate cps"
}

# Ensure the script is called with the output file
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <output_file>"
    exit 1
fi

# Call the function with the provided file
parse_sipp_output "$1"
