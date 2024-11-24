OUTPUT_FILE = "sipp_output.log"
ERROR_FILE = None


NCpS = 200
INTERVAL_TIME = 5
COMMAND = "./sipp -sf client.xml 192.168.21.45 -m 1000 -r 200 -d 1s -inf numbers.csv"

def update_command(command, r):
    # COMMAND[7]: new call per second
    # COMMAND[5]: max number of calls in testing
    command[7] = str(r)
    command[5] = str(INTERVAL_TIME*r)
    return command
# "-trace_err",

'''run the command '''
import subprocess
def run_sipp_command(r = NCpS):
    command = COMMAND.split()
    command = update_command(command, r)
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    with open(OUTPUT_FILE, "w") as file:
        file.write(result.stdout)

'''fail rate calculation on client side'''
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



if __name__ == "__main__":
    command = COMMAND.split()
    print("NewCall per Second Test\n")
    mc = input(f"Kamailio Server ({command[3]}): ")
    if mc:
        command[3] = mc
    sf = input(f"With Scenario File ({command[2]}): ")
    if sf:
        command[2] = sf
    it = input(f"Inerval Time ({INTERVAL_TIME}): ")
    if it:
        INTERVAL_TIME = sf

    sn = input("Starting Rate (200): ")
    if sn:
        NCpS = int(sn)

    COMMAND = " ".join(command)


    n = input("Max Rate (500): ")
    if not n:
        n = 500
    else: n=int(n)

    step = input("Increase Rate (10): ")
    if not step:
        step = 10
    else: step=int(step)

    print("-"*30, "TEST STARTED")

    f1 = 0
    f2 = 0
    for r in range(NCpS, n+1, step):
        print(f"Rate: {r}", end=", ")
        run_sipp_command(r)

        # find_latest_error_file()

        total_calls, fail_rate = parse_sipp_output()
        print(f"Failed: {fail_rate:2f}%")

        # error_dict = parse_sipp_error_log()
        if fail_rate > 0.1 and not f1:
            print(f"Max ideal rate = {r - step}")
            f1 = 1
        elif fail_rate > 1 and not f2:
            print(f"Max safe rate = {r - step}")
            f2 = 1
        elif fail_rate > 10:
            print(f"Disaster rate = {r}")
            print("-"*30, "TEST FINISHED")
            break
    # run_sipp_command()
