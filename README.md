# Build & Run RTPENGINE in kernel mode


Other possibly working method to install on Ubuntu: [Link](https://nickvsnetworking.com/rtpengine-installation-configuration-ubuntu-20-04-22-04/)

## Build
1. Clone this [repo](https://github.com/sipwise/rtpengine)
-  Following the instructions in the official [document](https:/rtpengine.readthedocs.io/en/latest/compiling_and_installing.html) for installation:
2. Install the requirements (You may need to install some packages manually)
3. `sudo apt-get install pkg-config libglib2.0-dev zlib1g-dev libssl-dev libpcre3-dev libxmlrpc-core-c3-dev libhiredis-dev gperf libcurl4-openssl-dev libevent-dev libpcap-dev libsystemd-dev libspandsp-dev libmariadb-dev libiptc-dev ffmpeg libavcodec-dev libavfilter-dev libswresample-dev libbcg729-0-dev libmosquitto-dev libwebsockets-dev libopus-dev`
4. At the top directory of `./rtpengine` run `make` (If the requirements are all satisfied, It will build successfully)
5.  If you need to use kernel mode:
	- run `make` in `./rtpengine/kernel-module`
	- `insmod xt_RTPENGINE.ko`
	- `sudo cp xt_RTPENGINE.ko /lib/modules/$(uname -r)/
	- `sudo modprobe xt_RTPENGINE`

## Run
- Following the instructions in the official [document]( https://rtpengine.readthedocs.io/en/latest/usage.html ) for setup and usage:
1. Configure `rtpengine` in `./rtpengine/etc/rtpengine.conf`:
	- `table = 0` (or any other number for `iptable`/`nftable` on kernel mode)
	- `table = -1` for not allowing kernel module
	- `interface` and `listen-*` parameters should be set according to the machines you are running on
2. At the top directory of `/rtpengine` run `./daemon/rtpengine --foreground --config-file ./etc/rtpengine.conf --pidfile=rtpengine.pid` to run the daemon
3. To see the status of `rtpengine`. (If the kernel mode is active or not):
	- `ls /procat /proc/rtpengine/0/status` to see the status
	-  ls `/proc/rtpengine/` (If the table number `0` (or any other) does not exists, kernel mode is deactivated)
	- `cat /proc/rtpengine/0/list` to see the running rules on streams. Run this when testing calls to see the forwarding RTP streams
	- To see rule set on `nftable`: `sudo nft list ruleset` (look for `rtpengine).` (The `XT target RTPENGINE not found` is normal !)
	- To see the rule set on `iptables` : `iptables -L -v -n`
	- To see if the kernel module is loaded: `lsmod | grep xt_RTPENGINE`
	- Attention: running on this mode and not with installed packages and `systemctl`, on stopping the process, `rtpengine` exits. the important logs are displayed where the daemon command is running
	- To check the CPU status of `rtpeninge`: `pidstat -p $(pidstat | grep rtpengine | awk '{print $4}') 1`

# Testing RTPENGINE, Checking performance & quality with SIPP

## Test steps:

1. initialize `rtpengine` on the correct configue: 
	- `./daemon/rtpengine --foreground --config-file ./etc/rtpengine.conf --no-fallback --pidfile=rtpengine.pid`
2. check if correct config:
	- `cat /proc/rtpengine/0/list` in same machine as rtpengine
	- `No such file or directory` in user-space mode and null or rtp list on kernel mode
3. capture cpu usage
	- `pidstat -p $(pidstat | grep rtpengine | awk '{print $4}') 1` optional: `> storefile.log`
4. capture rtp streams
	- `tcpdump -i any -w test.pcacp`
4.  compose kamailio
	- initialize pcscf on the same host machine as rtpengine
5. on sipp server machine:
	-  `./sipp -sf server.xml -inf p2.csv 192.168.21.83:5060 -mi 192.168.21.57 -p 6070 -mp 20000 -m 2000`
6. on sipp client machine:
	- `./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 20s -r 50 -rp 1s -m 2000`
7. wait till sipp is finished and then stop the capture




## مراحل انجام شده برای تست CPU

انجام تست‌های مختلف در حالت kernel mode و userspace mode و مقایسه نمودار cpu usage آنها



تعداد تماس های جدید ایجاد شده در cpu usage موثر است. و بهتر است اگر مسئله تماس همزمان است، از تعداد ساخت کمتر استفاده شود.



Packer loss in RTP streams are too high
-> changing network adapter to test
on range 100

changing all commands from `192.168.21.*` to `192.168.100.*`
- kamailio.cfg
- rtprngine.conf
- rtpengine_test.sh & server-performance.sh
- test_rtpengine.py


`./daemon/rtpengine --foreground --config-file ./etc/rtpengine.conf --no-fallback --pidfile=rtpengine.pid > ./rtpengine.log 2>&1`

for saving `rtpengine` output




`pidstat -C "kamailio|rtpengine" 1`


`python3 analysis/rtp-analyse.py test900_capture.pcap > test900_res.txt`


------------- We need to tune the os for high packet