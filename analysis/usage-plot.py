import pandas as pd
import matplotlib.pyplot as plt
import sys

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
def plot_total_cpu_comparison(df1, df2=None):
    df1, label1 = df1

    plt.figure(figsize=(10, 6))

    # Plot total CPU usage for the first log file
    plt.plot(df1.index, df1['total_cpu'], label=f'{label1} total CPU', color='blue')

    try:
        # Plot total CPU usage for the second log file
        df2, label2 = df2
        plt.plot(df2.index, df2['total_cpu'], label=f'{label2} total CPU', color='green')
    except:
        pass

    # Formatting the plot
    plt.xlabel('Log Entry (Step)')
    plt.ylabel('Total CPU Usage (%)')
    plt.title('Comparison of total CPU usage across log entries (aligned by CPU spike)')
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.tight_layout()
    plt.show()

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("input log file")
        sys.exit(1)
    
    log_file1 = sys.argv[1]
    df1_total_cpu = process_pidstat_total_cpu(log_file1, threshold=10.0)

    try:
        log_file2 = sys.argv[2]
        df2_total_cpu = process_pidstat_total_cpu(log_file2, threshold=10.0)
    except:
        df2_total_cpu = None


        plot_total_cpu_comparison((df1_total_cpu, "Log File 1"), (df2_total_cpu, "Log File 2"))
        
    # Process the two pidstat log files for total CPU usage
    

    # Plot the total CPU usage comparison
    
