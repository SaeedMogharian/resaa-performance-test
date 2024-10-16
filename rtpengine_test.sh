#!/bin/bash

# Function to find the closest factors of a number
find_closest_factors() {
    local n=$1
    local sqrt_n=$(echo "sqrt($n)" | bc)

    for (( x=sqrt_n; x>0; x-- )); do
        if (( n % x == 0 )); then
            y=$(( n / x ))
            echo "$x $y"
            return
        fi
    done
}

# Check if the correct number of arguments is provided
if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <natural_number>"
    exit 1
fi

# Get the input
n=$1

# Calculate m
m=$(( n * 2 ))

# Find closest factors
read x y < <(find_closest_factors $n)

# Determine the smaller and larger factors
if (( x < y )); then
    smaller=$x
    larger=$y
else
    smaller=$y
    larger=$x
fi

# Construct and execute the SIP command
sipp_command="./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d ${larger}s -r ${smaller} -rp 1s -m $m"
echo "Executing command: $sipp_command"
eval $sipp_command
