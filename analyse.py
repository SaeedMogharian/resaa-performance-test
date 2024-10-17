import sys
import subprocess
import pandas as pd
from dataclasses import dataclass
import re


@dataclass
class QualityConfig:
    packets: int
    lost_percent: float
    jitter: float


@dataclass
class AnalyzeReportStream:
    fail: int = 0
    valid: int = 0
    jitter: int = 0
    lost: int = 0

    @property
    def all(self):
        return self.fail + self.valid


def run_command(command):
    """Runs a shell command with error handling."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)


def generate_csv_file_header(csv_file):
    """Generates the header for the CSV file."""
    header = ('start time,end time,src ip,src port,des ip,des port,SSRC,payload,packets,lost,lost percent,'
              'min delta,mean delta,max delta,min jitter,mean jitter,max jitter')
    command = f"echo '{header}' > {csv_file}"
    run_command(command)


def generate_csv_file_content(csv_file, pcap_file):
    """Generates the content for the CSV file by parsing the pcap file with tshark."""
    command = (f"tshark -r {pcap_file} -qz rtp,streams | head -n -1 | tail -n +3 | "
               f"sed 's/X//' | sed 's/^[[:space:]]*//;s/[[:space:]]\\{{1,\\}},/g' | sed 's/,$//' >> {csv_file}")
    run_command(command)


def create_csv_file(csv_file, pcap_file):
    """Creates a CSV file with header and content."""
    generate_csv_file_header(csv_file)
    generate_csv_file_content(csv_file, pcap_file)


def analyze_stream(data_frame, quality_config: QualityConfig):
    """Analyzes the RTP streams based on the quality configuration."""
    report = AnalyzeReportStream()

    for index in data_frame.index:
        # Check packet count
        if data_frame.loc[index, "packets"] < quality_config.packets:
            data_frame.drop(index, inplace=True)
            report.fail += 1
            continue

        # Check jitter
        if data_frame.loc[index, "mean jitter"] > quality_config.jitter:
            report.jitter += 1

        # Check lost percentage (clean parsing)
        lost_percent_str = re.sub(r"[^\d.]", "", str(data_frame.loc[index, "lost percent"]))
        if float(lost_percent_str) > quality_config.lost_percent:
            report.lost += 1

    report.valid = len(data_frame)
    return report


def is_pass_test(report: AnalyzeReportStream):
    """Determines if the test passes based on jitter and packet loss."""
    return report.jitter == 0 and report.lost == 0


def print_report(report: AnalyzeReportStream, quality_config: QualityConfig):
    """Prints the analysis report."""
    print("------------------------------")
    print(f"Valid streams : {report.valid}")
    print(f"Failed streams: {report.fail}")
    print(f"Total streams : {report.all}")
    print("------------------------------")
    print(f"Invalid jitter: {report.jitter} (>{quality_config.jitter})")
    print(f"Lost invalid  : {report.lost} (>{quality_config.lost_percent}%)")
    print("------------------------------")
    print("Test Pass" if is_pass_test(report) else "Test Not Pass")
    print("------------------------------")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Input pcap file")
        sys.exit(1)

    print("Creating CSV file")
    csv_file = "file.csv"
    pcap_file = sys.argv[1]

    create_csv_file(csv_file, pcap_file)

    print("Analyzing Quality")
    quality_config = QualityConfig(packets=20, lost_percent=0.5, jitter=30.0)

    data_frame = pd.read_csv(csv_file)
    report = analyze_stream(data_frame, quality_config)
    print_report(report, quality_config)
