import subprocess
import os
import signal
import time
import sys
from threading import Thread

# Function to read PID from a file
def get_pid_from_file(pid_file):
    try:
        with open(pid_file, 'r') as file:
            pid = file.read().strip()
            return pid
    except FileNotFoundError:
        print(f"PID file {pid_file} not found.")
        return None
    except Exception as e:
        print(f"Error reading PID file {pid_file}: {e}")
        return None

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
def stop_daemon(daemon_process):
    try:
        os.killpg(os.getpgid(daemon_process.pid), signal.SIGTERM)  
        print(f"Daemon process with PID {daemon_process.pid} terminated.")
    except Exception as e:
        print(f"Failed to stop daemon process: {e}")

def check_rtpengine_log(log_file_path):
    """Monitor the rtpengine.log file for new content."""
    with open(log_file_path, "r") as log_file:
        # Move the cursor to the end of the file
        log_file.seek(0, os.SEEK_END)

        while True:
            line = log_file.readline()
            if line:
                print("test is aborted: ", line.strip())
                # Abort the test by terminating the program
                os._exit(1)  # This forcefully exits all threads and processes
            time.sleep(1)  # Adjust this sleep interval if necessary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("input concurrent call number")
        sys.exit(1)
    try:
        test_id = sys.argv[2] 
    except:
        test_id = "9"
    n = sys.argv[1] 

    sipp_server = "root@192.168.21.57"
    sipp_client = "root@192.168.21.56"

    project_dir = os.path.expanduser("/root/projects/rtpengine_performance_test")
    
    # Path to the PID file
    pid_file_path = "/root/projects/rtpengine/rtpengine/rtpengine.pid"
    log_file_path = "/root/projects/rtpengine/rtpengine/rtpengine.log"  # Path to rtpengine.log

    # Start a thread to monitor the rtpengine log file
    log_thread = Thread(target=check_rtpengine_log, args=(log_file_path,))
    log_thread.daemon = True
    log_thread.start()

    # Read the PID from the file
    rtpengine_pid = get_pid_from_file(pid_file_path)

    if rtpengine_pid:
        # If the PID is found, proceed with pidstat
        pidstat_command = ["pidstat", "-p", rtpengine_pid, "1"]
        pidstat_dir = os.path.expanduser("/root/projects/rtpengine_performance_test")
        pidstat_log_file = os.path.join(pidstat_dir, f"test{test_id}_pidstat_log.log")
        
        # Run pidstat and redirect output to a log file
        pidstat_process = run_daemon(pidstat_command, pidstat_dir, log_file=pidstat_log_file)
        time.sleep(3)

        tcpdump_log_file = f"test{test_id}_tcpdump.pcap"
        tcpdump_command = ["tcpdump", "-i",  "any",  "-w", tcpdump_log_file ]
        tcpdump_dir = os.path.expanduser("/root/projects/rtpengine_performance_test")
        tcpdump_process = run_daemon(tcpdump_command, tcpdump_dir)
        time.sleep(3)

    
        # Run remote commands
        server_command = ["./server-performance.sh", str(int(n)*2)]
        sipp_dir = os.path.expanduser("/root/saeedm/performance-test")
        server_process = run_remote_daemon(server_command, sipp_server, "a", working_directory=sipp_dir)
        time.sleep(3)

        client_command = ["./rtpengine_test.sh", str(n)]
        client_process = run_remote_daemon(client_command, sipp_client, "a", working_directory=sipp_dir)
        time.sleep(3)

        # Wait for client command to finish
        print("Waiting for the client process to complete...")
        client_process.wait()  # Block until client_command finishes

        # Once client command finishes, stop pidstat
        time.sleep(3)

        print(f"Client command finished. Stopping pidstat... Logs saved in {pidstat_log_file}")
        stop_daemon(pidstat_process)
        time.sleep(3)
        print(f"Stopping tcpdump... Saved in {tcpdump_log_file}")
        stop_daemon(tcpdump_process)
        time.sleep(3)
    else:
        print("RTPengine PID not found. Unable to start pidstat.")