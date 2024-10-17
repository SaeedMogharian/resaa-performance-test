import pandas as pd
import matplotlib.pyplot as plt

# Function to read and process a pidstat log file for total CPU usage
def process_pidstat_total_cpu(file_path, threshold=10.0):
    # Read the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Initialize lists for storing the extracted data
    total_cpu_data = []

    # Extract relevant data from each line
    for line in lines:
        if line.startswith("Average:"):
            continue  # skip the average lines
        columns = line.split()
        if len(columns) > 6:
            try:
                total_cpu = float(columns[5])  # Extract %CPU (total usage)
                total_cpu_data.append(total_cpu)
            except:
                continue

    # Create a DataFrame with the extracted data
    df = pd.DataFrame({'total_cpu': total_cpu_data})

    # Find the first index where CPU usage increases significantly
    start_index = df[df['total_cpu'] > threshold].first_valid_index()

    # Return the DataFrame sliced from the detected start index
    if start_index is not None:
        df = df.loc[start_index:].reset_index(drop=True)

    return df

# Function to plot total CPU usage comparison
def plot_total_cpu_comparison(df1, df2, label1, label2):
    plt.figure(figsize=(10, 6))

    # Plot total CPU usage for the first log file
    plt.plot(df1.index, df1['total_cpu'], label=f'{label1} total CPU', color='blue')

    # Plot total CPU usage for the second log file
    plt.plot(df2.index, df2['total_cpu'], label=f'{label2} total CPU', color='green')

    # Formatting the plot
    plt.xlabel('Log Entry (Step)')
    plt.ylabel('Total CPU Usage (%)')
    plt.title('Comparison of total CPU usage across log entries (aligned by CPU spike)')
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    plt.show()


import os
if __name__=="__main__":
    # Example usage:
    
    home="C:/Users/Resaa/OneDrive/Resaa/MGW/rtpengine_performance_test/"
    t1_k_nfb = 'test1_kernel-mode_no-fallback.log'
    t1_k = 'test1_kernel-mode_normal.log'
    t1_u = 'test1_userspace-mode.log'
    t2_k_nfb = 'test2_kernel-mode_no-fallback.log'
    t2_k = 'test2_kernel-mode_normal.log'
    t2_u = 'test2_userspace-mode.log'
    t3_k_nfb = 'test3_kernel-mode_no-fallback.log'
    t4_k_nfb = 'test4_kernel-mode.log'
    t4_u = 'test4_user-mode.log'
    t5_k_nfb = 'test5_kernel-mode.log'
    t5_u = 'test5_user-mode.log'
    t6_k_nfb = 'test6_kernel-mode.log'
    t7_k_nfb = 'test7_kernel-mode.log'



    # file_path1 = home + t6_k_nfb
    file_path1 = home + t5_u
    file_path2 = home + t5_k_nfb

    # Process the two pidstat log files for total CPU usage
    df1_total_cpu = process_pidstat_total_cpu(file_path1, threshold=10.0)
    df2_total_cpu = process_pidstat_total_cpu(file_path2, threshold=10.0)

    # Plot the total CPU usage comparison
    plot_total_cpu_comparison(df1_total_cpu, df2_total_cpu, 'Log File 1', 'Log File 2')
