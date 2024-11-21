ماشین kamailio:
192.168.21.45
ماشین sipp server
192.168.21.57
ماشین sipp client
192.168.21.56

### SIPP-SIPP Test 1-1:
##### rate 4110 c/s:
retrans = 0
##### rate 4120 c/s:
retrans = 35/20000
fail rate = 0
##### rate 4150 c/s:
retrans = 8/20000
fail rate = 0
##### rate 4180 c/s:
retrans = 18/20000
fail rate = 0

server:
```bash
./sipp -sf server.xml
```
client:
```bash
./sipp -sf client.xml 192.168.21.57
```

### SIPP-SIPP Test 1000-1000:
(client.xml with field)
[[Kamailio cps test/Test/client.xml]]
[[Kamailio cps test/Test/server.xml]]
##### rate 3000 c/s:
retrans = 0/20000

``` bash
./sipp -sf client.xml 192.168.21.57 -m 20000 -inf numbers.csv -r 3000
```
numbers.csv:
```csv
SEQUENTIAL
8000;8001
8002;8003
8004;8005
8006;8007
...
...
...
9998;9999
```

Peak was 2944 calls, after 6 s
Peak was 8739 calls, after 8 s
##### rate 3100 c/s:
retrans = 5/20000
failed calls = 5/20000


### SIPP Kamailio Tests 1-1:
```bash
##client
./sipp -sf client.xml 192.168.21.45 -m 1000 -r 100

##server
./sipp -sf server.xml 192.168.21.45
```
#### rate: 240 c/s
Failed calls = 0/1000
retrans = 0

#### rate: 250 c/s
Failed Calls on BYE: 5/1000
retrans = 0
#### Max safe rate: 400 c/s
Failed Calls: 36/5000 < 1%
#### rate: 420 c/s
Failed Calls: 50/10000 = 5%
retrans = 0
#### Disaster rate: 450 c/s
30 calls does not reach server!
Failed rate = 675/5000 > 10%

### SIPP Kamailio Tests 1000-1000:
(client.xml with field)
```bash
./sipp -sf client.xml 192.168.21.45 -m 1000 -r 250 -d 1s -inf numbers.csv
```
#### rate: 240 c/s
Failed calls = 0/10000
retrans = 0
#### rate: 250 c/s
Failed Calls on BYE: 3/10000
retrans = 0
#### Max safe rate: 400 c/s
Failed Calls on BYE: 67/10000 < 1%
retrans = 0
#### Disaster rate: 450 c/s
720/1000 calls does not reach server!
Failed rate = 1423/10000 > 10%







## Script
```bash
./sipp -sf client.xml 192.168.21.45 -d 1s -rate_increase 20 -rate_interval 10s -rate_max 500 -inf numbers.csv -trace_err -r 10
```

Python Script:
```python
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
from datetime import datetime
def parse_sipp_output():
	with open(OUTPUT_FILE, 'r') as file:
		data = file.read()
	# Extract Cumulative Successful and Failed Calls
	successful_calls_match = re.search(r"Successful call\s+\|\s+[^\|]+\|\s+(\d+)", data)
	successful_calls = int(successful_calls_match.group(1).strip()) if successful_calls_match else 0
	failed_calls_match = re.search(r"Failed call\s+\|\s+[^\|]+\|\s+(\d+)", data)
	failed_calls = int(failed_calls_match.group(1).strip()) if failed_calls_match else 0
	# Calculate total calls and failed call rate
	total_calls = successful_calls + failed_calls
	failed_call_rate = (failed_calls / total_calls) * 100 if total_calls > 0 else 0
	return (total_calls,failed_call_rate)

  
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
	if not n: n = 500
	else: n=int(n)
	step = input("Increase Rate (10): ")
	if not step: step = 10
	else: step=int(step)
	print("-"*30, "TEST STARTED")
	f1 = 0
	f2 = 0
	for r in range(NCpS, n+1, step):
		print(f"Rate: {r}", end=", ")
		run_sipp_command(r)
		
		total_calls, fail_rate = parse_sipp_output()
		print(f"Failed: {fail_rate:2f}%")
		
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

```


cps_test.txt (test_output):
```
NewCall per Second Test
Kamailio Server (192.168.21.45):
With Scenario File (client.xml):
Inerval Time (5):
Starting Rate (200):
Max Rate (500):
Increase Rate (10):
------------------------------ TEST STARTED
Rate: 200, Failed: 0.000000%
Rate: 210, Failed: 0.000000%
Rate: 220, Failed: 0.000000%
Rate: 230, Failed: 0.000000%
Rate: 240, Failed: 0.000000%
Rate: 250, Failed: 0.080000%
Rate: 260, Failed: 0.000000%
Rate: 270, Failed: 0.074074%
Rate: 280, Failed: 0.000000%
Rate: 290, Failed: 0.137931%
Max ideal rate = 280
Rate: 300, Failed: 0.200000%
Rate: 310, Failed: 0.064516%
Rate: 320, Failed: 0.125000%
Rate: 330, Failed: 0.121212%                               
Rate: 340, Failed: 0.058824%                               
Rate: 350, Failed: 0.057143%                               
Rate: 360, Failed: 0.111111%                               
Rate: 370, Failed: 0.108108%                               
Rate: 380, Failed: 0.210526%                               
Rate: 390, Failed: 0.256410%                               
Rate: 400, Failed: 0.150000%                               
Rate: 410, Failed: 2.439024%                               
Max safe rate = 400                                        
Rate: 420, Failed: 7.047619%                               
Rate: 430, Failed: 0.139535%                               
Rate: 440, Failed: 0.136364%                               
Rate: 450, Failed: 2.177778%                               
Rate: 460, Failed: 7.260870%                               
Rate: 470, Failed: 12.340426%                              
Disaster rate = 470                                        
------------------------------ TEST FINISHED    
```

