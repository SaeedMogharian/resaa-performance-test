#!/bin/bash

# Check if the user provided an argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <count> <> "
    exit 1
fi

# Read the call number from the command-line argument
n=$1

echo "Testing register.xml scnario on sipp n times with users.csv"

# Correct the variable assignment without spaces around the equals sign
SIPP_CLIENT_CMD="./sipp -sf register.xml -inf users.csv 172.16.100.74 -m ${n}"
SIPP_CLIENT_DIR="/root/sipp"
original_dir=$(pwd)

# Run the SIPp client command and capture its output
cd ${SIPP_CLIENT_DIR} && ${SIPP_CLIENT_CMD} > "${original_dir}/${n}_sipp_client.log" 

# Run the parse_sipp_output script with the log file
cd ${original_dir} && python3 parse_sipp_output.py "${n}_sipp_client.log"
