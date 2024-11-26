#!/bin/bash

# Prompt the user to enter the starting number
read -p "Enter the starting number: " start_number

# Loop to run testing.sh 10 times, incrementing n by 10 each time
for ((n = start_number; n < start_number + 100; n += 10)); do
    # Run the testing.sh script with the current value of n
    echo "Running testing.sh with n=$n..."
    
    # Pass the value of n to testing.sh by setting it as an environment variable
    export n
    ./testing.sh
    
    # Optionally, add a delay between iterations if necessary
    sleep 1
done
