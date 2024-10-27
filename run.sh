#!/bin/bash

# Check if an argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <argument>"
  exit 1
fi

# Store the argument in a variable
n=$1
echo "Argument received: $n"

## Run the first Python file with the argument
#echo "Running test_rtpengine.py with argument $n..."
#python3 test_rtpengine.py "$n"
#if [ $? -ne 0 ]; then
#  echo "Error: test_rtpengine.py failed."
#  exit 1
#fi
#echo "Successfully ran test_rtpengine.py with argument $n."

# Run the second Python file, redirecting output to "test$n.txt"
echo "Running rtp-analyse.py with test$n.pcap, outputting to test$n.txt..."
python3 ./analysis/rtp-analyse.py "test$n.pcap" > "test$n.txt"
if [ $? -ne 0 ]; then
  echo "Error: rtp-analyse.py failed."
  exit 1
fi
echo "Successfully ran rtp-analyse.py, output saved to test$n.txt."

# Remove the file "test$n.pcap"
echo "Removing test$n.pcap..."
rm "test$n.pcap"
if [ $? -ne 0 ]; then
  echo "Error: failed to remove test$n.pcap."
  exit 1
fi
echo "Successfully removed test$n.pcap."

# Run the usage plot script
echo "Running usage-plot.py with test$n.log..."
python3 ./analysis/usage-plot.py "test$n.log"
if [ $? -ne 0 ]; then
  echo "Error: usage-plot.py failed."
  exit 1
fi
echo "Successfully ran usage-plot.py with test$n.log."

# Move output files to the "test" directory
#echo "Moving output files test$n* to ./test/..."
#mv "test$n"* "./test/"
#if [ $? -ne 0 ]; then
#  echo "Error: failed to move output files to ./test/."
#  exit 1
#fi
#echo "Output files successfully moved to ./test/."
