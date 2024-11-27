#!/bin/bash

# Check if the user provided an argument
if [ $# -lt 1 ]; then
    echo "Usage: $0 <scenario> <remote-host> <count>"
    exit 1
fi

source config

# Read the call number from the command-line argument
scenario="${CONFIG_FILES_DIR}/${1}.xml"
remote=$2
n=1


echo "Testing ${scenario} scenario on sipp ${n} times with ${INFO_FILE}"

# Correct the variable assignment without spaces around the equals sign
sipp_cmd="./sipp -sf ${scenario} -inf ${CONFIG_FILES_DIR}/${INFO_FILE} ${remote} -m ${n}"
original_dir=$(pwd)

# Run the SIPp client command and capture its output
cd ${SIPP_DIR} && ${sipp_cmd} > "${original_dir}/${n}_sipp_client.log" 

# Run the parse_sipp_output script with the log file
cd ${original_dir} && python3 parse_sipp_output.py "${n}_sipp_client.log"
