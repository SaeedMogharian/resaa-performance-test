import sys
import subprocess
import pandas as pd
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
    unpaired_ssrc: int = 0

    @property
    def all(self):
        return self.fail + self.valid


def run_command(command):
    subprocess.run(command, shell=True)


def genarate_csv_file_header(csv_file):
    command = f"echo 'start time,end time,src ip,src port,des ip,des port,SSRC,payload,packets,lost,lost percent,min delta,mean delta,max delta,min jitter,mean jitter,max jitter' > {csv_file}"
    run_command(command=command)


def genarate_csv_file_content(csv_file, pcap_file):
    command = f"tshark -r {pcap_file} -qz rtp,streams | head -n -1 | tail -n +3 | sed 's/X//' | sed 's/^[[:space:]]*//;s/[[:space:]]\\{{1,\\}}/,/g'| sed 's/,$//' >> {csv_file}"
    run_command(command=command)


def create_csv_file(csv_file, pcap_file):
    genarate_csv_file_header(csv_file)
    genarate_csv_file_content(csv_file, pcap_file)


def analyze_stream(data_frame, quality_config: QualityConfig):
    report = AnalyzeReportStream()

    # Group by SSRC and check if each SSRC appears exactly twice (paired)
    ssrc_counts = data_frame['SSRC'].value_counts()

    for ssrc, count in ssrc_counts.items():
        if count != 2:
            report.unpaired_ssrc += 1

    for index in data_frame.index:
        if data_frame.loc[index, "packets"] < quality_config.packets:
            data_frame.drop(index, inplace=True)
            report.fail += 1
            continue

        if data_frame.loc[index, "mean jitter"] > quality_config.jitter:
            report.jitter += 1

        if float(data_frame.loc[index, "lost percent"][1:-2]) > quality_config.lost_percent:
            report.lost += 1

    report.valid = len(data_frame)
    return report


def is_pass_test(report: AnalyzeReportStream):
    if report.jitter == 0 and report.lost == 0 and report.unpaired_ssrc == 0:
        return True
    return False


def print_report(report: AnalyzeReportStream, quality_config: QualityConfig):
    print("------------------------------")
    print(f"valid stream : {report.valid}")
    print(f"broken stream: {report.fail}")
    print(f"all streams: {report.all}")
    print(f"unpaired SSRCs: {report.unpaired_ssrc}")
    print("------------------------------")
    print(f"jitter invalid: {report.jitter} (>{quality_config.jitter})")
    print(f"lost invalid: {report.lost} (>{quality_config.lost_percent}%)")
    print("------------------------------")
    if is_pass_test(report):
        print("Test Pass")
    else:
        print("Test Not Pass")
    print("------------------------------")

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("input pcap file")
    #     sys.exit(1)

    print("Create csv file")
    csv_file ="file.csv"
    # pcap_file = sys.argv[1] 
    pcap_file = "/root/projects/rtpengine_performance_test/analysis/failed-capture.pcap"

    create_csv_file(csv_file, pcap_file)
    
    print("Analyze Quality")
    quality_config = QualityConfig(packets=20, lost_percent=0.5, jitter=30.0)
    
    data_frame = pd.read_csv(csv_file)
    report: AnalyzeReportStream = analyze_stream(data_frame, quality_config)
    print_report(report, quality_config)
        


