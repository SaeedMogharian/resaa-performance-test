import subprocess
import os
import time
import sys
from threading import Thread


# Function to run a command as a daemon on a remote machine using SSH and password
def run_remote_daemon(command, remote, password, working_directory):
    ssh_command = [
        "sshpass", "-p", password, "ssh", f"{remote}",
        f"cd {working_directory} && nohup {' '.join(command)} &"
    ]
    
    daemon_process = subprocess.Popen(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print(f"Daemon process started with SSH command: {' '.join(ssh_command)}")
    return daemon_process

# Function to run a local daemon and capture output
def run_daemon(command, working_directory, log_file=None):
    stdout = open(log_file, 'w') if log_file else subprocess.PIPE
    stderr = subprocess.PIPE
    
    daemon_process = subprocess.Popen(
        command, 
        stdout=stdout, 
        stderr=stderr, 
        preexec_fn=os.setsid,  
        cwd=working_directory
    )
    
    print(f"Daemon process {' '.join(command)} executed in directory {working_directory}")
    return daemon_process

# Function to stop the daemon process
def check_rtpengine_log(log_file):
    """Monitor the rtpengine.log file for new content."""
    with open(log_file, "r") as logs:
        # Move the cursor to the end of the file
        logs.seek(0, os.SEEK_END)

        while True:
            line = logs.readline()
            if line:
                print("\n\ntest is failed and aborted: ", line.strip())
                # Abort the test by terminating the program
                kill_process("kamailio")
                kill_process("rtpengine")
                kill_process("tcpdump")
                kill_process("pidstat")
                os._exit(1)  # This forcefully exits all threads and processes
            time.sleep(1)  # Adjust this sleep interval if necessary

def kill_process(target):
    def _by_pid(pid):
        try:
            subprocess.run(['kill', '-9', pid], check=True)
            print(f"Killed process with PID: {pid}")
        except OSError as e:
            print(f"Error killing process with PID {pid}: {e}")

    def _by_name(program_name):
        try:
            # Find PIDs for the program name using pidstat and grep
            result = subprocess.run(f"pidstat | grep {program_name} | awk '{{print $4}}'", shell=True, capture_output=True, text=True)
            # Check if any PIDs were found
            if result.returncode != 0 or not result.stdout.strip():
                print(f"No processes found for program: {program_name}")
                return
            # Split the output by lines to get each PID
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                _by_pid(pid)
        except Exception as e:
            print(f"Error finding/killing processes by name '{program_name}': {e}")

    def _by_obj(daemon_process):
        if isinstance(daemon_process, subprocess.Popen):
            _by_pid(daemon_process.pid)
        else:
            print(f"Invalid Popen object: {daemon_process}")

    def handle_target(target):
        # Handle each type of target: int/str (PID), subprocess.Popen, or program name (str)
        if isinstance(target, int) or (isinstance(target, str) and target.isdigit()):
            _by_pid(target)  # If the target is a PID
        elif isinstance(target, subprocess.Popen):
            _by_obj(target)  # If the target is a Popen object
        elif isinstance(target, str):
            _by_name(target)  # If the target is a program name
        else:
            print(f"Unsupported target type: {type(target)}")

    # Process a single item or list
    if isinstance(target, list):
        for item in target:
            handle_target(item)
    else:
        handle_target(target)

def read_config(file_path):
    config = {}
    with open(file_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):  # Ignore empty lines and comments
                key, value = line.strip().split('=', 1)
                config[key.strip()] = value.strip()
    return config


if __name__ == "__main__":
    project_dir = os.getcwd()
    config = read_config(f'{project_dir}/.env')


    print(config)

    log_file_path = f"{project_dir}/rtpengine.log"  # Path to rtpengine.log

    if len(sys.argv) < 2:
        print("input call count")
        sys.exit(1)
    a = sys.argv[1]

    try:
        b = sys.argv[2] 
    except:
        b = str(int(a)+1)

    

    for n in range(int(a),int(b),100):
        kill_process("kamailio")
        kill_process("rtpengine")
        time.sleep(8)

        rtpengine_command = (config["RTPENGINE_CMD"]+ f" > {log_file_path} 2>&1").split()
        rtpengine_process = run_daemon(rtpengine_command, config["RTPENGINE_DIR"])
        time.sleep(5)

        kamailio_process = run_daemon(config["KAMAILIO_CMD"].split(), config["KAMAILIO_DIR"])
        time.sleep(15)


        test_id = n
        

        # Start a thread to monitor the rtpengine log file
        log_thread = Thread(target=check_rtpengine_log, args=(log_file_path,))
        log_thread.daemon = True
        log_thread.start()

        res = subprocess.run(f"pidstat | grep rtpengine | awk '{{print $4}}'", shell=True, capture_output=True, text=True)
        rtpengine_pid = res.stdout.strip().split('\n')

        if not rtpengine_pid:
            print("RTPengine PID not found. Unable to start the test.")
            exit(0)


        # If the PID is found, proceed with pidstat
        pidstat_command = ["pidstat", "-p", rtpengine_pid, "1"]
        pidstat_log_file = f"{project_dir}/test{test_id}_usage.log"
        pidstat_process = run_daemon(pidstat_command, project_dir, log_file=pidstat_log_file)
        time.sleep(3)


        print(f"Testing on n={n}")

        tcpdump_log_file = f"test{test_id}_capture.pcap"
        tcpdump_command = ["tcpdump", "-i",  "any",  "-w", tcpdump_log_file ]
        tcpdump_process = run_daemon(tcpdump_command, project_dir)
        time.sleep(3)


        # Run remote commands
        server_command = f"{config['SIPP_SERVER_CMD']} {n}".split()
        server_process = run_remote_daemon(server_command,
                                           f"{config['SIPP_SERVER_USER']}@{config['SIPP_SERVER']}",
                                           config['SIPP_SERVER_PASSWORD'], working_directory=config['SIPP_SERVER_DIR'])
        time.sleep(3)

        client_command = f"{config['SIPP_CLIENT_CMD']} {n}".split()
        client_process = run_remote_daemon(client_command,
                                           f"{config['SIPP_CLIENT_USER']}@{config['SIPP_CLIENT']}",
                                           config['SIPP_CLIENT_PASSWORD'], working_directory=config['SIPP_CLIENT_DIR'])
        time.sleep(3)

        # Wait for client process to finish
        print("Waiting for the client process to complete...")
        client_process.wait()  # Block until client_command finishes

        print(f"Stopping pidstat... Logs saved in {pidstat_log_file}")
        kill_process(pidstat_process)
        time.sleep(3)

        print(f"Stopping tcpdump... Saved in {tcpdump_log_file}")
        kill_process(tcpdump_process)
        time.sleep(3)

    








        