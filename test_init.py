import subprocess
import os
import signal

# Function to run a command as a daemon on a remote machine using SSH and password
def run_remote_daemon(command, remote, password):
    ssh_command = ["sshpass", "-p", password, "ssh", f"{remote}", "nohup"] + command + ["&"]
    daemon_process = subprocess.Popen(ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Daemon process started on {remote} with SSH command: {' '.join(ssh_command)}")
    return daemon_process

# Function to run a local daemon and capture output
def run_daemon(command, working_directory, output_file, capture_output=False):
    stdout = subprocess.PIPE if capture_output else None
    stderr = subprocess.PIPE if capture_output else None
    
    # Start the command as a background process (detaching it from the main process)
    daemon_process = subprocess.Popen(command, stdout=stdout, stderr=stderr, preexec_fn=os.setsid, cwd=working_directory)
    print(f"Daemon process started with PID {daemon_process.pid} in directory {working_directory}")

    # Capture output if requested
    if capture_output:
        with open(output_file, 'w') as f:
            while True:
                output = daemon_process.stdout.readline()
                if output == b'' and daemon_process.poll() is not None:
                    break
                if output:
                    f.write(output.decode())
                    f.flush()  # Ensure output is written to the file immediately
        print(f"Output saved to {output_file}")

    return daemon_process

# Function to stop the daemon process
def stop_daemon(daemon_process):
    try:
        os.killpg(os.getpgid(daemon_process.pid), signal.SIGTERM)  # Send SIGTERM to the process group
        print(f"Daemon process with PID {daemon_process.pid} terminated.")
    except Exception as e:
        print(f"Failed to stop daemon process: {e}")

import time
# Main function with sequential stopping of processes after client command finishes
if __name__ == "__main__":
    test_id = "9"
    n = 1500

    sipp_server = "root@192.168.21.57"
    sipp_client = "root@192.168.21.56"

    rtpengine_dir = os.path.expanduser("~/projects/rtpengine/rtpengine")
    rtpengine_command = [
        "./daemon/rtpengine",
        "--foreground",
        "--config-file", "./etc/rtpengine.conf",
        "--no-fallback",
        "--pidfile=rtpengine.pid"
    ]

    # Run local daemons and capture output
    rtpengine_process = run_daemon(rtpengine_command, rtpengine_dir, capture_output=True)
    time.sleep(5)

    pidstat_command = ["pidstat", "-p", str(rtpengine_process.pid), "1"]
    pidstat_dir = os.path.expanduser("/root/projects/rtpengine_performance_test")
    pidstat_process = run_daemon(pidstat_command, pidstat_dir, capture_output=True)

    kamailio_dir = os.path.expanduser("/root/projects/resaa-pcscf")
    kamailio_command = ["docker", "compose", "up"]
    kamailio_process = run_daemon(kamailio_command, kamailio_dir)

    # Run remote commands
    server_command = ["~/saeedm/performance-test/server-performance.sh", str(n*2)]
    server_process = run_remote_daemon(server_command, sipp_server, "a")

    client_command = ["~/saeedm/performance-test/rtpengine_test.sh", str(n)]
    client_process = run_remote_daemon(client_command, sipp_client, "a")

    # Wait for client command to finish
    print("Waiting for the client process to complete...")
    client_process.wait()  # Block until client_command finishes

    # Once client command finishes, stop pidstat and save its output to a file
    time.sleep(3)

    print("Client command finished. Stopping pidstat...")
    stop_daemon(pidstat_process, log_file="pidstat_output.log")
    time.sleep(5)


    # Stop rtpengine daemon and save its output to a file
    print("Stopping rtpengine daemon...")
    stop_daemon(rtpengine_process, log_file="rtpengine_output.log")
    time.sleep(5)

    # Stop kamailio daemon (no output capture for kamailio)
    print("Stopping kamailio daemon...")
    stop_daemon(kamailio_process)
