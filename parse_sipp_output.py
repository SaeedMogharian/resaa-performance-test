import re
import os

def parse_sipp_output(output_file):
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"The file {output_file} does not exist.")
    
    with open(output_file, 'r') as file:  
        data = file.read()

    def extract_value(pattern, default=0):
        match = re.search(pattern, data)
        return int(match.group(1).strip()) if match else default

    successful_calls = extract_value(r"Successful call\s+\|\s+[^\|]+\|\s+(\d+)")
    failed_calls = extract_value(r"Failed call\s+\|\s+[^\|]+\|\s+(\d+)")
    total_calls = successful_calls + failed_calls
    failed_call_rate = (failed_calls / total_calls) * 100 if total_calls > 0 else 0

    call_rate_match = re.search(r"Call Rate\s+\|\s+[^\|]+\|\s+([\d.]+)", data)
    call_rate = float(call_rate_match.group(1).strip()) if call_rate_match else 0.0

    return (total_calls,
            failed_calls
    )
import sys
if __name__=="__main__":
    if len(sys.argv) < 2:
        print("input sipp output file")
        sys.exit(1)

    file = sys.argv[1]

    total_calls, fail_rate = parse_sipp_output(file)
    print(f"On total calls = {total_calls}, Failed: {fail_rate:2f}%")
