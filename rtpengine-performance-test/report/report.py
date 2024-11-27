import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# Directory where the text files are stored
directory = '../test/'  # Replace with the path containing the files



# Initialize lists to store extracted data
file_names = []
all_streams = []
valid_streams = []
failed_calls = []
broken_streams = []
unpaired_ssrcs = []
jitter_invalid = []
lost_invalid = []

# Loop over each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r') as file:
            content = file.read()

            # Extract relevant metrics using regex
            all_streams_value = int(re.search(r'All streams: (\d+)', content).group(1))
            valid_streams_value = int(re.search(r'Valid streams : (\d+)', content).group(1))
            failed_calls_value = int(re.search(r'Failed calls: (\d+)', content).group(1))
            broken_streams_value = int(re.search(r'Broken streams: (\d+)', content).group(1))
            unpaired_ssrcs_value = int(re.search(r'Unpaired SSRCs: (\d+)', content).group(1))
            jitter_invalid_value = int(re.search(r'Jitter invalid: (\d+)', content).group(1))
            lost_invalid_value = int(re.search(r'Lost invalid: (\d+)', content).group(1))

            # Append to lists
            # file_names.append(filename)
            # all_streams.append(all_streams_value)
            # valid_streams.append(valid_streams_value)
            # failed_calls.append(failed_calls_value)
            # broken_streams.append(broken_streams_value)
            # unpaired_ssrcs.append(unpaired_ssrcs_value)
            # jitter_invalid.append(jitter_invalid_value)
            # lost_invalid.append(lost_invalid_value)

            file_names.append(filename)
            all_streams.append(all_streams_value)
            valid_streams.append((valid_streams_value / all_streams_value) * 100)
            failed_calls.append((failed_calls_value / all_streams_value) * 100)
            broken_streams.append((broken_streams_value / all_streams_value) * 100)
            unpaired_ssrcs.append((unpaired_ssrcs_value / all_streams_value) * 100)
            jitter_invalid.append((jitter_invalid_value / all_streams_value) * 100)
            lost_invalid.append((lost_invalid_value / all_streams_value) * 100)

# Create DataFrame
data = {
    'File Name': file_names,
    'All Streams': all_streams,
    'Valid Streams': valid_streams,
    'Failed Calls': failed_calls,
    'Broken Streams': broken_streams,
    'Unpaired SSRCs': unpaired_ssrcs,
    'Jitter Invalid': jitter_invalid,
    'Lost Invalid': lost_invalid
}

df = pd.DataFrame(data)
print("Summary Table:")
# markdown_file_path = 'summary_metrics.md'
# with open(markdown_file_path, 'w') as md_file:
#     md_file.write("# Metrics Summary\n\n")
#     md_file.write("The following table provides a summary of the metrics from each file.\n\n")
#     md_file.write(df.to_markdown(index=False))
# print(f"DataFrame saved to {markdown_file_path}")
print(df)




# Save and display the table
# from ace_tools import display_dataframe_to_user
# display_dataframe_to_user(name="Detailed Summary of Metrics", dataframe=df)

# Plot each attribute
attributes = [
    'All Streams', 'Valid Streams', 'Failed Calls',
    'Broken Streams', 'Unpaired SSRCs', 'Jitter Invalid', 'Lost Invalid'
]
for attribute in attributes:
    plt.figure()
    plt.bar(df['File Name'], df[attribute])
    plt.xlabel('File Name')
    if attribute != "All Streams":
        plt.ylabel(f"{attribute} %")
    plt.title(f'{attribute} per File')
    plt.xticks(rotation=45)
    plt.tight_layout()
    # plt.show()
    output_path= f"Q-{attribute}.png"
    plt.savefig(output_path, format='png')