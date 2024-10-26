#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <argument>"
  exit 1
fi

# Store the argument in a variable
n=$1

# Run the first Python file with the argument
python3 test_rtpengine.py "$n"
if [ $? -ne 0 ]; then
  echo "Error: test_rtpengine.py failed."
  exit 1
fi

# Run the second Python file, redirecting output to "test$n.txt"
python3 ./analysis/rtp-analyse.py "test$n.pcap" > "test$n.txt"
if [ $? -ne 0 ]; then
  echo "Error: script2.py failed."
  exit 1
fi

# Remove the file "test$n.pcap"
rm "test$n.pcap"
if [ $? -ne 0 ]; then
  echo "Error: failed to remove test$n.pcap."
  exit 1
fi
