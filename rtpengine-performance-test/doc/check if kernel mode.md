sTo check if RTPengine is routing packets to userspace or performing kernel forwarding correctly, you can follow these steps:

### 1. **Check the RTPengine Mode**

RTPengine can work in either userspace or kernel mode, depending on how it's configured. You can check which mode RTPengine is operating in by reviewing its startup parameters or configuration:

- **Userspace Mode**: In userspace mode, RTP packets are processed by the RTPengine daemon running in user space, which involves more overhead and higher latency.
- **Kernel Mode**: In kernel mode, RTPengine interacts directly with the kernel's packet forwarding mechanisms (Netfilter) for faster, lower-latency forwarding.

To confirm that RTPengine is running in kernel mode, you can check the command used to start RTPengine. Look for the `--no-fallback` flag, which ensures that RTPengine operates in kernel mode without falling back to userspace.

For example, if RTPengine is started with the following arguments:

```bash
rtpengine --interface=eth0 --listen-ng=127.0.0.1:2223 --no-fallback
```

This ensures that RTPengine is working in kernel mode, and will not fall back to userspace if kernel forwarding fails.

### 2. **Check for Active Kernel Forwarding**

In kernel mode, RTPengine forwards RTP packets directly using the Netfilter hooks and does not hand over RTP packet handling to the userspace daemon unless there's an issue. You can verify this by:

- **Checking `/proc/rtpengine/`**: If you see session entries in `/proc/rtpengine/`, this indicates that RTPengine is handling packets at the kernel level. You can check for active sessions and monitor packet statistics.

For example:

```bash
cat /proc/rtpengine/0/list
```

Look for packet counters and session details. If packet counters are increasing and no errors are present, this indicates kernel-based forwarding is functioning properly.

- **Packet Statistics**: Use `nftables` or `iptables` rules to count packets processed by the `rtpengine` chain. This can help confirm that RTP packets are being processed as expected.

```bash
nft list ruleset | grep rtpengine
```

or

```bash
iptables -L -v | grep rtpengine
```

Look at the packet counters to verify that the RTP packets are being routed through the `rtpengine` chain, which would indicate kernel forwarding.

### 3. **Monitoring RTP Traffic in Userspace**

If RTPengine is routing traffic to userspace, you'll see RTP packet handling in the RTPengine logs. You can monitor the RTPengine logs to see if RTP packets are being processed in userspace.

To do this, check the system logs or RTPengine logs, typically located in `/var/log/rtpengine.log` or by running `journalctl`:

```bash
journalctl -u rtpengine.service
```

Look for any indications of packets being handled in userspace. If kernel mode is functioning properly, there should be minimal userspace activity related to RTP packet processing.

### 4. **Check Packet Flow with `tcpdump`**

To ensure that packets are being routed correctly (either through kernel forwarding or userspace), you can use `tcpdump` to monitor the actual RTP traffic flowing through your network interfaces.

```bash
tcpdump -i <interface> udp port <RTP port>
```

Replace `<interface>` with the name of the interface you want to monitor (e.g., `eth0`), and `<RTP port>` with the RTP port range used by RTPengine.

Monitor the incoming and outgoing packets. If you see consistent forwarding with no delays, it indicates that the RTP packets are being processed correctly, most likely in kernel mode.

### 5. **Check System Load**

Kernel mode packet forwarding typically results in lower CPU usage compared to userspace mode. You can monitor the system's CPU load to get an indication of how the packets are being processed:

- **Userspace Mode**: Higher CPU usage because packets are handled by the RTPengine daemon.
- **Kernel Mode**: Lower CPU usage because most of the packet processing happens in the kernel.

Use a tool like `top` or `htop` to monitor CPU usage by RTPengine. If the system load is low, it's likely that kernel forwarding is working as expected.

```bash
htop
```

Check if the `rtpengine` process is consuming significant CPU. Low CPU usage suggests that RTPengine is offloading most packet forwarding to the kernel.

### 6. **Check for Errors in Kernel Logs**

If RTPengine is not performing kernel forwarding correctly, there might be error messages in the kernel logs. Use `dmesg` or `journalctl` to check for any errors related to RTPengine or Netfilter:

```bash
dmesg | grep rtpengine
```

or

```bash
journalctl -k | grep rtpengine
```

Look for any error messages related to Netfilter hooks or kernel packet forwarding issues.

### 7. **Test Fallback to Userspace**

One way to confirm that kernel forwarding is working is to simulate a failure and observe if RTPengine falls back to userspace processing. If you remove the `--no-fallback` option from the startup command, RTPengine will fall back to userspace if kernel forwarding fails.

You can also temporarily disable kernel forwarding (e.g., by unloading the RTPengine kernel module) and see if RTPengine starts processing RTP packets in userspace.

### Summary

To check if RTPengine is correctly routing packets in kernel mode:

1. **Verify startup parameters** (check for `--no-fallback` flag).
2. **Inspect `/proc/rtpengine/`** to see kernel-level session tracking.
3. **Monitor Netfilter rules** (`nftables` or `iptables`) to ensure RTP packets are being processed.
4. **Use `tcpdump`** to capture RTP packet flow.
5. **Check CPU usage** for low load (kernel mode).
6. **Check logs** (`dmesg`, `journalctl`) for kernel-level errors.
7. **Test fallback to userspace** if kernel forwarding is disabled.

Let me know if you need further assistance in monitoring your setup!