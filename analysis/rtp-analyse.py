import sys
import subprocess
import csv
from dataclasses import dataclass


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
    subprocess.run(command, shell=True)


def generate_csv_file_header(csv_file):
    command = f"echo 'start time,end time,src ip,src port,des ip,des port,SSRC,payload,packets,lost,lost percent,min delta,mean delta,max delta,min jitter,mean jitter,max jitter' > {csv_file}"
    run_command(command=command)


def generate_csv_file_content(csv_file, pcap_file):
    command = f"tshark -r {pcap_file} -qz rtp,streams | head -n -1 | tail -n +3 | sed 's/X//' | sed 's/^[[:space:]]*//;s/[[:space:]]\{{1,\}}/,/g'| sed 's/,$//' >> {csv_file}"
    run_command(command=command)


def create_csv_file(csv_file, pcap_file):
    generate_csv_file_header(csv_file)
    generate_csv_file_content(csv_file, pcap_file)


def analyze_stream(csv_file, quality_config: QualityConfig):
    report = AnalyzeReportStream()

    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            try:
                packets = int(row['packets'])
                mean_jitter = float(row['mean jitter'])
                lost_percent = float(row['lost percent'].strip('%'))

                # Check packet count
                if packets < quality_config.packets:
                    report.fail += 1
                    continue
                
                # Check jitter
                if mean_jitter > quality_config.jitter:
                    report.jitter += 1
                
                # Check lost percentage
                if lost_percent > quality_config.lost_percent:
                    report.lost += 1

                report.valid += 1

            except (ValueError, KeyError) as e:
                # Skip row if there are missing or malformed fields
                report.fail += 1
                continue

    return report


def is_pass_test(report: AnalyzeReportStream):
    return report.jitter == 0 and report.lost == 0


def print_report(report: AnalyzeReportStream, quality_config: QualityConfig):
    print("------------------------------")
    print(f"Valid streams : {report.valid}")
    print(f"Broken streams : {report.fail}")
    print(f"Total streams : {report.all}")
    print("------------------------------")
    print(f"Jitter invalid : {report.jitter} (>{quality_config.jitter})")
    print(f"Lost invalid : {report.lost} (>{quality_config.lost_percent}%)")
    print("------------------------------")
    if is_pass_test(report):
        print("Test Pass")
    else:
        print("Test Not Pass")
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

    # Process the CSV file line by line
    report: AnalyzeReportStream = analyze_stream(csv_file, quality_config)
    print_report(report, quality_config)
