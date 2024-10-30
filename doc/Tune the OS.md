https://github.com/sorooshm78/system-telephony?tab=readme-ov-file#linux
# Linux
## Interrupts
### Links

* [Understanding CPU Interrupts](https://alibaba-cloud.medium.com/understanding-cpu-interrupts-in-linux-8af22d6e548a)
* [Receive-Side Scaling (RSS)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/performance_tuning_guide/network-rss#doc-wrapper)
* [Receive Packet Steering (RPS)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/performance_tuning_guide/network-rps)
* [Receive Flow Steering (RFS)](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/performance_tuning_guide/network-rfs)
* [CPU affinity calculator](https://bitsum.com/tools/cpu-affinity-calculator)


### Understanding CPU Interrupts
### What Is an Interrupt?
When a hardware component (such as a disk controller or an Ethernet NIC) needs to interrupt the work of the CPU, it triggers an interrupt. The interrupt notifies the CPU that an event occurred and the CPU should suspend its current work to deal with the event. To prevent multiple devices from sending the same interrupt, Linux provides an interrupt request system so that each device in the computer system is assigned an interrupt number to ensure the uniqueness of its interrupt request.

In kernel 2.4 and later, Linux improves the capability of assigning specific interrupts to the specified processors (or processor groups). This is called the SMP IRQ affinity, which controls how the system responds to various hardware events. You can limit or redistribute the server workload so that the server can work more efficiently.

Let’s take NIC interrupts as an example. Without the SMP IRQ affinity, all NIC interrupts are associated with CPU 0. As a result, CPU 0 is overloaded and cannot efficiently process network packets, causing a bottleneck in performance.

After you configure the SMP IRQ affinity, multiple NIC interrupts are allocated to multiple CPUs to distribute the CPU workload and speed up data processing. The SMP IRQ affinity requires NICs to support multiple queues. A NIC supporting multiple queues has multiple interrupt numbers, which can be evenly allocated to different CPUs.

You can simulate a multi-queue mode for a single-queue NIC by means of receive packet steering (RPS) or receive flow steering (RFS), but the effect is poorer than that of a multi-queue NIC with RPS/RFS enabled.


### What Are RPS and RFS?
Receive packet steering (RPS) balances the load of soft interrupts among CPUs. In short, the NIC driver calculates a hash ID for each stream by using a quadruplet (SIP, SPORT, DIP, and DPORT), and the interrupt handler allocates the hash ID to the corresponding CPU, thus fully utilizing the multi-core capability. Generally, RPS simulates functions of a multi-queue NIC by using software. If a NIC supports multiple queues, RPS is ineffective. RPS is mainly intended for single-queue NICs in a multi-CPU environment. If a NIC supports multiple queues, you can directly bind hard interrupts to CPUs by configuring the SMP IRQ affinity.

![](https://miro.medium.com/v2/resize:fit:828/format:webp/0*Tjj5kzCpNcuuVvtR.png)

RPS simply distributes data packets to different CPUs. This greatly degrades the utilization of CPU caches when different CPUs are used to run applications and handle soft interrupts. In this case, RFS ensures that one CPU is used to run applications and handle soft interrupts, to fully utilize the CPU caches. RPS and RFS are usually used together to achieve the best results. They are mainly intended for single-queue NICs in a multi-CPU environment.

![](https://miro.medium.com/v2/resize:fit:828/format:webp/0*YDvx-JGgtipsUl3z.png)

The values of rps_flow_cnt and rps_sock_flow_entries are carried to the nearest power of 2. For a single-queue device, rps_flow_cnt is equal to rps_sock_flow_entries.

Receive flow steering (RFS), together with RPS, inserts data packets into the backlog queue of a specified CPU, and wakes up the CPU for execution.

IRQbalance is applicable to most scenarios. However, in scenarios requiring high network performance, you are recommended to bind interrupts manually.

IRQbalance can cause some issues during operation:

* The calculated value is sometimes inappropriate, failing to achieve load balancing among CPUs.

* When the system is idle and IRQs are in power-save mode, IRQbalance distributes all interrupts to the first CPU, to make other idle CPUs sleep and reduce energy consumption. When the load suddenly rises, performance may be degraded due to the lag in adjustment.

* The CPU specified to handle interrupts frequently changes, resulting in more context switches.

* IRQbalance is enabled but does not take effect, that is, does not specify a CPU for handling interrupts.

### Receive-Side Scaling (RSS)
Receive-Side Scaling (RSS), also known as multi-queue receive, distributes network receive processing across several hardware-based receive queues, allowing inbound network traffic to be processed by multiple CPUs. RSS can be used to relieve bottlenecks in receive interrupt processing caused by overloading a single CPU, and to reduce network latency.

To determine whether your network interface card supports RSS, check whether multiple interrupt request queues are associated with the interface in /proc/interrupts. For example, if you are interested in the p1p1 interface:

```
# egrep 'CPU|p1p1' /proc/interrupts
      CPU0    CPU1    CPU2    CPU3    CPU4    CPU5
89:   40187       0       0       0       0       0   IR-PCI-MSI-edge   p1p1-0
90:       0     790       0       0       0       0   IR-PCI-MSI-edge   p1p1-1
91:       0       0     959       0       0       0   IR-PCI-MSI-edge   p1p1-2
92:       0       0       0    3310       0       0   IR-PCI-MSI-edge   p1p1-3
93:       0       0       0       0     622       0   IR-PCI-MSI-edge   p1p1-4
94:       0       0       0       0       0    2475   IR-PCI-MSI-edge   p1p1-5
```

The preceding output shows that the NIC driver created 6 receive queues for the p1p1 interface (p1p1-0 through p1p1-5). It also shows how many interrupts were processed by each queue, and which CPU serviced the interrupt. In this case, there are 6 queues because by default, this particular NIC driver creates one queue per CPU, and this system has 6 CPUs. This is a fairly common pattern amongst NIC drivers.

Alternatively, you can check the output of `ls -1 /sys/devices/*/*/device_pci_address/msi_irqs` after the network driver is loaded. For example, if you are interested in a device with a PCI address of 0000:01:00.0, you can list the interrupt request queues of that device with the following command:

```
# ls -1 /sys/devices/*/*/0000:01:00.0/msi_irqs
101
102
103
104
105
106
107
108
109
```

RSS is enabled by default. The number of queues (or the CPUs that should process network activity) for RSS are configured in the appropriate network device driver. For the bnx2x driver, it is configured in num_queues. For the sfc driver, it is configured in the rss_cpus parameter. Regardless, it is typically configured in /sys/class/net/device/queues/rx-queue/, where device is the name of the network device (such as eth1) and rx-queue is the name of the appropriate receive queue.

When configuring RSS, Red Hat recommends limiting the number of queues to one per physical CPU core. Hyper-threads are often represented as separate cores in analysis tools, but configuring queues for all cores including logical cores such as hyper-threads has not proven beneficial to network performance.

When enabled, RSS distributes network processing equally between available CPUs based on the amount of processing each CPU has queued. However, you can use the ethtool --show-rxfh-indir and --set-rxfh-indir parameters to modify how network activity is distributed, and weight certain types of network activity as more important than others.

The irqbalance daemon can be used in conjunction with RSS to reduce the likelihood of cross-node memory transfers and cache line bouncing. This lowers the latency of processing network packets. If both irqbalance and RSS are in use, lowest latency is achieved by ensuring that irqbalance directs interrupts associated with a network device to the appropriate RSS queue.


### Receive Packet Steering (RPS)
Receive Packet Steering (RPS) is similar to RSS in that it is used to direct packets to specific CPUs for processing. However, RPS is implemented at the software level, and helps to prevent the hardware queue of a single network interface card from becoming a bottleneck in network traffic.

RPS has several advantages over hardware-based RSS:
* RPS can be used with any network interface card.
* It is easy to add software filters to RPS to deal with new protocols.
* RPS does not increase the hardware interrupt rate of the network device. However, it does introduce inter-processor interrupts.

RPS is configured per network device and receive queue, in the /sys/class/net/device/queues/rx-queue/rps_cpus file, where device is the name of the network device (such as eth0) and rx-queue is the name of the appropriate receive queue (such as rx-0).

The default value of the rps_cpus file is zero. This disables RPS, so the CPU that handles the network interrupt also processes the packet.

To enable RPS, configure the appropriate rps_cpus file with the CPUs that should process packets from the specified network device and receive queue.

The rps_cpus files use comma-delimited CPU bitmaps. Therefore, to allow a CPU to handle interrupts for the receive queue on an interface, set the value of their positions in the bitmap to 1. For example, to handle interrupts with CPUs 0, 1, 2, and 3, set the value of rps_cpus to 00001111 (1+2+4+8), or f (the hexadecimal value for 15).

For network devices with single transmit queues, best performance can be achieved by configuring RPS to use CPUs in the same memory domain. On non-NUMA systems, this means that all available CPUs can be used. If the network interrupt rate is extremely high, excluding the CPU that handles network interrupts may also improve performance.

For network devices with multiple queues, there is typically no benefit to configuring both RPS and RSS, as RSS is configured to map a CPU to each receive queue by default. However, RPS may still be beneficial if there are fewer hardware queues than CPUs, and RPS is configured to use CPUs in the same memory domain.

### Receive Flow Steering (RFS)
Receive Flow Steering (RFS) extends RPS behavior to increase the CPU cache hit rate and thereby reduce network latency. Where RPS forwards packets based solely on queue length, RFS uses the RPS backend to calculate the most appropriate CPU, then forwards packets based on the location of the application consuming the packet. This increases CPU cache efficiency.

RFS is disabled by default. To enable RFS, you must edit two files:

```
/proc/sys/net/core/rps_sock_flow_entries
```

Set the value of this file to the maximum expected number of concurrently active connections. We recommend a value of 32768 for moderate server loads. All values entered are rounded up to the nearest power of 2 in practice.

```
/sys/class/net/device/queues/rx-queue/rps_flow_cnt
```

Replace device with the name of the network device you wish to configure (for example, eth0), and rx-queue with the receive queue you wish to configure (for example, rx-0).

Set the value of this file to the value of rps_sock_flow_entries divided by N, where N is the number of receive queues on a device. For example, if rps_flow_entries is set to 32768 and there are 16 configured receive queues, rps_flow_cnt should be set to 2048. For single-queue devices, the value of rps_flow_cnt is the same as the value of rps_sock_flow_entries.

Data received from a single sender is not sent to more than one CPU. If the amount of data received from a single sender is greater than a single CPU can handle, configure a larger frame size to reduce the number of interrupts and therefore the amount of processing work for the CPU. 

Alternatively, consider NIC offload options or faster CPUs.
Consider using numactl or taskset in conjunction with RFS to pin applications to specific cores, sockets, or NUMA nodes. This can help prevent packets from being processed out of order.

### Viewing in practical
System processing interrupts are recorded in the **/proc/interrupts** file
```
# cat /proc/interrupts
           CPU0       CPU1       CPU2       CPU3
  0:        141          0          0          0   IO-APIC-edge      timer
  1:         10          0          0          0   IO-APIC-edge      i8042
  4:        807          0          0          0   IO-APIC-edge      serial
  6:          3          0          0          0   IO-APIC-edge      floppy
  8:          0          0          0          0   IO-APIC-edge      rtc0
  9:          0          0          0          0   IO-APIC-fasteoi   acpi
 10:          0          0          0          0   IO-APIC-fasteoi   virtio3
 11:         22          0          0          0   IO-APIC-fasteoi   uhci_hcd:usb1
 12:         15          0          0          0   IO-APIC-edge      i8042
 14:          0          0          0          0   IO-APIC-edge      ata_piix
 15:          0          0          0          0   IO-APIC-edge      ata_piix
 24:          0          0          0          0   PCI-MSI-edge      virtio1-config
 25:       4522          0          0       4911   PCI-MSI-edge      virtio1-req.0
 26:          0          0          0          0   PCI-MSI-edge      virtio2-config
 27:       1913          0          0          0   PCI-MSI-edge      virtio2-input.0
 28:          3        834          0          0   PCI-MSI-edge      virtio2-output.0
 29:          2          0       1557          0   PCI-MSI-edge      virtio2-input.1
 30:          2          0          0        187   PCI-MSI-edge      virtio2-output.1
 31:          0          0          0          0   PCI-MSI-edge      virtio0-config
 32:       1960          0          0          0   PCI-MSI-edge      virtio2-input.2
 33:          2        798          0          0   PCI-MSI-edge      virtio2-output.2
 34:         30          0          0          0   PCI-MSI-edge      virtio0-virtqueues
 35:          3          0        272          0   PCI-MSI-edge      virtio2-input.3
 36:          2          0          0        106   PCI-MSI-edge      virtio2-output.3
input0 indicates the network interrupt handled by the first CPU (CPU 0).
If there are multiple Alibaba Cloud ECS network interrupts, input.1, input.2, and input.3 are available.
......
PIW:          0          0          0          0   Posted-interrupt 
```

**What is `/proc/irq/`?**
   - `/proc/irq/` is a virtual filesystem in Linux that provides information about interrupt requests (IRQs). IRQs are signals generated by hardware devices to notify the CPU that they need attention. Common examples include keyboard input, network card events, or disk I/O completion.
   - Each IRQ has its own directory within `/proc/irq/`, making it easy to inspect and configure specific interrupts.
   - It’s a technique in Linux that directs incoming network packets to specific CPUs for processing

**Contents of `/proc/irq/`:**
   - Inside each IRQ directory, you'll find files with useful information:
     - `smp_affinity`: Specifies which CPU cores can handle the IRQ. You can set CPU affinity using this file.
     - `smp_affinity_list`: Similar to `affinity`, but expressed as a bitmask (e.g., `0-3` for cores 0 to 3).

**Setting CPU Affinity:**
   - To improve performance, you can bind an IRQ to specific CPU cores. For example:
     ```bash
     echo 1 > /proc/irq/IRQ/smp_affinity
     ```
     This assigns the IRQ to CPU core 1. for calculate use this [link](https://bitsum.com/tools/cpu-affinity-calculator)
     
   - Use `cat /proc/irq/IRQ/smp_affinity` to check the current affinity.

**Bitmask:**
"f" is a hexadecimal value corresponding to the binary value of “1111”. (When the bits for four CPUs are set to f, all CPUs are used to handle interrupts.)

**Receive Packet Steering (RPS)** in Linux is a technique used to direct incoming network packets to specific CPUs for processing. It helps prevent the hardware queue of a single network interface card (NIC) from becoming a bottleneck in network traffic¹. Here's how you can configure RPS:

**Identify the CPUs** you want to use for packet processing. For example, if you want to use CPUs 0, 1, 2, and 3, set the value of `rps_cpus` to `00001111` (binary) or `f` (hexadecimal).

**Edit the configuration file** for your network interface. Typically, this file is located in `/sys/class/net/<interface_name>/queues/rx-<queue_number>/rps_cpus`. Replace `<interface_name>` with your actual NIC name and `<queue_number>` with the queue number you want to configure.

**Set the desired CPU mask**. For example, to use CPUs 0, 1, 2, and 3, you can run the following command (replace `<interface_name>` and `<queue_number>` accordingly):
```bash
echo f > /sys/class/net/<interface_name>/queues/rx-<queue_number>/rps_cpus
```

**Verify the configuration** by checking the contents of the `rps_cpus` file:
```bash
cat /sys/class/net/<interface_name>/queues/rx-<queue_number>/rps_cpus
```
It should display the same CPU mask you set earlier.

**Control the number of entries in the global table (rps_sock_flow_table) by using a kernel parameter:**
```
# sysctl -a |grep net.core.rps_sock_flow_entries
net.core.rps_sock_flow_entries = 0
# sysctl -w net.core.rps_sock_flow_entries=32768
net.core.rps_sock_flow_entries = 32768
```

if queue is 8 then 32768/8=4096

**Specify the number of entries in the hash table of each NIC queue:**
```
#  cat /sys/class/net/<interface_name>/queues/rx-<queue_number>/rps_flow_cnt
0
# echo 4096 > /sys/class/net/<interface_name>/queues/rx-<queue_number>/rps_flow_cnt
#  cat /sys/class/net/<interface_name>/queues/rx-<queue_number>/rps_flow_cnt
4096
```

## ethtool
ethtool is a command-line utility in Linux used for querying and controlling network device driver and hardware settings. It provides a variety of functions to modify network interface card (NIC) parameters, diagnose issues, and optimize network performance. 

### Basic Usage
The general syntax for using ethtool is:

```
ethtool [options] <interface>
```
Where `<interface>` is the name of the network interface you want to manage, such as eth0, eth1, etc.

The `-c` and `-C` options in `ethtool` are used to display and configure interrupt coalescing settings for a network interface, respectively.

### Interrupt Coalescing
Interrupt coalescing is a technique used to reduce the number of interrupts sent to the CPU by the network interface card (NIC). Instead of generating an interrupt for every single packet, the NIC waits until a certain condition is met, such as a specific number of packets received or a certain amount of time passed, before generating an interrupt. This can improve CPU efficiency and reduce overhead, especially in high-throughput environments.

### `-c` Option: Display Interrupt Coalescing Settings

The `-c` option is used to display the current interrupt coalescing settings for a specified network interface.

#### Syntax
``` bash
ethtool -c <interface>
```

#### Example
```bash
ethtool -c eth0
```

#### Output
The output will look something like this:

```plaintext
Coalesce parameters for eth0:
Adaptive RX: off
Adaptive TX: off
stats-block-usecs: 0
pkt-rate-low: 0
pkt-rate-high: 0

RX: 
  Usecs: 64
  Frames: 0
TX: 
  Usecs: 64
  Frames: 0
```

- **Adaptive RX/TX**: Indicates whether adaptive interrupt coalescing is enabled.
- **stats-block-usecs**: Time interval (in microseconds) for updating statistics blocks.
- **pkt-rate-low/high**: Packet rate thresholds for low and high packet rates.
- **RX Usecs/Frames**: Number of microseconds or frames before an RX interrupt is generated.
- **TX Usecs/Frames**: Number of microseconds or frames before a TX interrupt is generated.

### `-C` Option: Modify Interrupt Coalescing Settings

The `-C` option is used to set the interrupt coalescing parameters for a specified network interface.

#### Syntax
```bash
ethtool -C <interface> [parameter value]
```

Where the parameters can include:

- `rx-usecs N`: Set the number of microseconds to wait before generating an RX interrupt.
- `rx-frames N`: Set the number of frames to receive before generating an RX interrupt.
- `tx-usecs N`: Set the number of microseconds to wait before generating a TX interrupt.
- `tx-frames N`: Set the number of frames to transmit before generating a TX interrupt.
- `adaptive-rx on/off`: Enable or disable adaptive RX interrupt coalescing.
- `adaptive-tx on/off`: Enable or disable adaptive TX interrupt coalescing.
- `stats-block-usecs N`: Set the statistics block interval in microseconds.
- `pkt-rate-low N`: Set the low packet rate threshold.
- `pkt-rate-high N`: Set the high packet rate threshold.

#### Example
```bash
ethtool -C eth0 rx-usecs 128 tx-usecs 128
```

This command sets the interrupt coalescing delay to 128 microseconds for both RX and TX on the network interface `eth0`.

### Practical Considerations
- **Performance Tuning**: Adjusting interrupt coalescing settings can help optimize performance. For example, increasing the RX/TX usecs can reduce CPU overhead by decreasing the number of interrupts, but it might introduce a slight delay in packet processing.
- **Adaptive Coalescing**: Enabling adaptive interrupt coalescing allows the NIC to dynamically adjust coalescing parameters based on current traffic conditions, which can be useful in environments with varying traffic loads.
- **Testing and Monitoring**: After making changes, it’s important to monitor network performance and CPU usage to ensure that the adjustments have the desired effect without introducing new issues.

### Conclusion
Using the `-c` and `-C` options in `ethtool`, you can display and configure interrupt coalescing settings for network interfaces. This allows for fine-tuning of how and when interrupts are generated by the NIC, which can lead to improved CPU efficiency and overall network performance in various environments.

### rx-usecs
The rx-usecs parameter specifies the amount of time, in microseconds, that the network interface card (NIC) will wait before generating an interrupt after receiving a packet. This setting is part of the interrupt coalescing mechanism which helps in reducing the CPU load by limiting the number of interrupts.

Usage Example:
```
ethtool -C eth0 rx-usecs 128
```
This command sets the NIC to wait for 128 microseconds after receiving a packet before generating an interrupt.

### rx-frames
The rx-frames parameter specifies the number of packets (frames) that the NIC will wait to receive before generating an interrupt. This setting, like rx-usecs, is part of the interrupt coalescing mechanism.

Usage Example:
```
ethtool -C eth0 rx-frames 32
```

This command sets the NIC to wait until 32 packets have been received before generating an interrupt.

### adaptive-rx
The adaptive-rx parameter enables or disables adaptive interrupt coalescing for receive interrupts. When adaptive interrupt coalescing is enabled, the NIC dynamically adjusts the rx-usecs and rx-frames settings based on the current traffic load and conditions. This can optimize performance by balancing latency and CPU utilization more effectively than static settings.

Usage Example:
```
ethtool -C eth0 adaptive-rx on
```
This command enables adaptive RX interrupt coalescing on the NIC, allowing it to automatically adjust the coalescing parameters as needed.


### rx-flow-hash
```
ethtool -N ens1f0np0 rx-flow-hash udp4 sd
       rx-flow-hash tcp4|udp4|ah4|esp4|sctp4|tcp6|udp6|ah6|esp6|sctp6
       m|v|t|s|d|f|n|r...
              Configures the hash options for the specified flow
              type.

              m   Hash on the Layer 2 destination address of the rx packet.
              v   Hash on the VLAN tag of the rx packet.
              t   Hash on the Layer 3 protocol field of the rx packet.
              s   Hash on the IP source address of the rx packet.
              d   Hash on the IP destination address of the rx packet.
              f   Hash on bytes 0 and 1 of the Layer 4 header of the rx packet.
              n   Hash on bytes 2 and 3 of the Layer 4 header of the rx packet.
              r   Discard all packets of this flow type. When this option is
                  set, all other options are ignored
```

The `rx-flow-hash` option in `ethtool` is used to configure the Receive Flow Hash setting for a network interface. This setting determines how the NIC (Network Interface Card) distributes incoming packets across multiple receive queues when receive-side scaling (RSS) is enabled. RSS is a technology that allows for the distribution of network processing across multiple CPU cores to improve performance and throughput, particularly in high-speed network environments.

### Understanding RX Flow Hash

Receive Flow Hash is a method used to determine which receive queue an incoming packet should be placed into. This decision is based on certain fields in the packet headers, such as source and destination IP addresses, ports, and protocols. The hashing algorithm uses these fields to compute a hash value, which is then used to assign the packet to one of the available receive queues.

### Fields Used for Hashing

Common fields that might be used in the hash calculation include:
- Source IP address
- Destination IP address
- Source port
- Destination port
- Protocol type

### Configuring `rx-flow-hash` with `ethtool`

You can use `ethtool` to get and set the RX flow hash configuration. The syntax typically looks like this:

```sh
ethtool -n [interface]
ethtool -N [interface] rx-flow-hash tcp4 sdfn
```

- `ethtool -n [interface]`: Displays the current RX flow hash configuration for the specified network interface.
- `ethtool -N [interface] rx-flow-hash [parameters]`: Sets the RX flow hash configuration for the specified network interface.

### Example

Here's an example of how you might configure `rx-flow-hash`:

```sh
ethtool -N eth0 rx-flow-hash tcp4 sdfn
```

In this command:
- `eth0` is the name of the network interface.
- `tcp4` indicates that the configuration applies to IPv4 TCP traffic.
- `sdfn` is a string where each letter represents a different field to be used in the hash calculation:
  - `s` stands for source IP address.
  - `d` stands for destination IP address.
  - `f` stands for source port.
  - `n` stands for destination port.

You can use different combinations of these fields based on your specific requirements.

### Practical Usage

#### Displaying Current RX Flow Hash Settings

To see the current RX flow hash configuration, you can use:

```sh
ethtool -n eth0
```

This will display the current settings for how packets are hashed and distributed across receive queues.

#### Setting RX Flow Hash Settings

To set the RX flow hash configuration, you might use:

```sh
ethtool -N eth0 rx-flow-hash udp4 sdfn
```

In this command:
- `udp4` indicates that the configuration applies to IPv4 UDP traffic.
- `sdfn` specifies that the hash calculation will use the source IP, destination IP, source port, and destination port fields.

### Benefits of Configuring RX Flow Hash

1. **Improved Performance:** By distributing incoming packets more evenly across multiple receive queues and CPU cores, the system can handle higher network throughput and reduce the risk of a single core becoming a bottleneck.
2. **Better Load Balancing:** Properly configured RX flow hash settings ensure that network processing is evenly distributed, which can lead to more consistent performance under load.
3. **Enhanced Scalability:** For systems with multiple CPU cores and high-speed network interfaces, configuring RX flow hash helps to fully utilize the available hardware resources.

### Conclusion

Configuring `rx-flow-hash` with `ethtool` allows you to fine-tune how your network interface distributes incoming packets across multiple receive queues


### Type of rx-flow-hash
The `rx-flow-hash` parameter in `ethtool` is used to configure how a network interface card (NIC) distributes incoming packets across multiple receive queues. This distribution helps to balance the load among multiple CPU cores and improve network performance. The `rx-flow-hash` types specify which fields of the packet headers are used to compute the hash value for this distribution.

Here are the common types of `rx-flow-hash` you might encounter:

### Common Types of RX Flow Hash

1. **IPV4 (ip4)**
   - `src`: Source IP address
   - `dst`: Destination IP address

2. **TCP over IPV4 (tcp4)**
   - `src`: Source IP address
   - `dst`: Destination IP address
   - `src-port`: Source port
   - `dst-port`: Destination port

3. **UDP over IPV4 (udp4)**
   - `src`: Source IP address
   - `dst`: Destination IP address
   - `src-port`: Source port
   - `dst-port`: Destination port

4. **SCTP over IPV4 (sctp4)**
   - `src`: Source IP address
   - `dst`: Destination IP address
   - `src-port`: Source port
   - `dst-port`: Destination port

5. **IPV6 (ip6)**
   - `src`: Source IP address
   - `dst`: Destination IP address

6. **TCP over IPV6 (tcp6)**
   - `src`: Source IP address
   - `dst`: Destination IP address
   - `src-port`: Source port
   - `dst-port`: Destination port

7. **UDP over IPV6 (udp6)**
   - `src`: Source IP address
   - `dst`: Destination IP address
   - `src-port`: Source port
   - `dst-port`: Destination port

8. **SCTP over IPV6 (sctp6)**
   - `src`: Source IP address
   - `dst`: Destination IP address
   - `src-port`: Source port
   - `dst-port`: Destination port

### Example Configuration

When configuring `rx-flow-hash` using `ethtool`, you specify the protocol and the fields to be used in the hash computation. For example:

```sh
ethtool -N eth0 rx-flow-hash tcp4 sdfn
```

In this command:
- `eth0` is the network interface.
- `tcp4` specifies the protocol (TCP over IPV4).
- `sdfn` is the combination of fields to use for the hash:
  - `s`: Source IP address
  - `d`: Destination IP address
  - `f`: Source port
  - `n`: Destination port

### Detailed Explanation of Each Field

1. **Source IP Address (`s`):** The IP address of the sender. Including this in the hash helps to distinguish traffic from different sources.
2. **Destination IP Address (`d`):** The IP address of the receiver. Including this helps to distinguish traffic destined for different addresses.
3. **Source Port (`f`):** The port number on the sender's side. This is especially useful for differentiating between multiple connections from the same source IP.
4. **Destination Port (`n`):** The port number on the receiver's side. This helps to distinguish different services (e.g., HTTP, HTTPS) running on the same destination IP.

### Practical Uses and Benefits

- **Load Balancing:** By using a combination of IP addresses and port numbers, you can ensure a more even distribution of packets across receive queues and CPU cores.
- **Scalability:** Proper configuration allows the system to handle higher network loads efficiently.
- **Performance:** Reduces bottlenecks by spreading the network processing workload, leading to better utilization of hardware resources.

### Conclusion

Configuring `rx-flow-hash` correctly can significantly enhance the performance and scalability of your network by ensuring an efficient distribution of incoming packets across multiple receive queues and CPU cores. This is particularly important in high-speed networking environments where optimal resource utilization is crucial.

### field of rx-flow-hash
The `rx-flow-hash` parameter in `ethtool` specifies how incoming packets are distributed across multiple receive queues by defining the fields used to compute a hash value. These fields are extracted from packet headers and used to generate a hash that determines the receive queue to which a packet will be assigned. This distribution helps to balance the load among multiple CPU cores, improving network performance.

Here's an explanation of the fields you can use in `rx-flow-hash`:

### Common Fields of RX Flow Hash

1. **Source IP Address (`s`):**
   - The IP address of the sender.
   - Used to distinguish traffic coming from different source IPs.
   - Applicable to both IPv4 (`ip4`, `tcp4`, `udp4`, `sctp4`) and IPv6 (`ip6`, `tcp6`, `udp6`, `sctp6`) protocols.

2. **Destination IP Address (`d`):**
   - The IP address of the receiver.
   - Used to distinguish traffic going to different destination IPs.
   - Applicable to both IPv4 (`ip4`, `tcp4`, `udp4`, `sctp4`) and IPv6 (`ip6`, `tcp6`, `udp6`, `sctp6`) protocols.

3. **Source Port (`f`):**
   - The port number on the sender's side.
   - Helps differentiate between multiple connections from the same source IP.
   - Applicable to transport layer protocols like TCP (`tcp4`, `tcp6`), UDP (`udp4`, `udp6`), and SCTP (`sctp4`, `sctp6`).

4. **Destination Port (`n`):**
   - The port number on the receiver's side.
   - Helps distinguish different services (e.g., HTTP, HTTPS) running on the same destination IP.
   - Applicable to transport layer protocols like TCP (`tcp4`, `tcp6`), UDP (`udp4`, `udp6`), and SCTP (`sctp4`, `sctp6`).

5. **IP Protocol (`i`):**
   - The protocol number from the IP header.
   - Used to differentiate traffic based on the protocol type (e.g., TCP, UDP).
   - Typically used in IPv4 and IPv6 configurations.

6. **VLAN Tag (`v`):**
   - The VLAN tag associated with the packet.
   - Helps differentiate traffic belonging to different VLANs.
   - Applicable in networks using VLANs for segmentation.

7. **Flow Label (`l`):**
   - The flow label field in the IPv6 header.
   - Used to identify specific flows in IPv6 traffic.
   - Applicable only to IPv6 configurations.

### Example Configurations

When configuring `rx-flow-hash` using `ethtool`, you can specify the protocol and the fields to be used in the hash computation. Here are some examples:

#### Example 1: TCP over IPv4 with Source and Destination IP and Ports

```sh
ethtool -N eth0 rx-flow-hash tcp4 sdfn
```

- `eth0` is the network interface.
- `tcp4` specifies the protocol (TCP over IPv4).
- `sdfn` indicates that the hash should be computed using:
  - `s`: Source IP address
  - `d`: Destination IP address
  - `f`: Source port
  - `n`: Destination port

#### Example 2: IPv6 with Source and Destination IP

```sh
ethtool -N eth0 rx-flow-hash ip6 sd
```

- `eth0` is the network interface.
- `ip6` specifies the protocol (IPv6).
- `sd` indicates that the hash should be computed using:
  - `s`: Source IP address
  - `d`: Destination IP address

### Practical Considerations

- **Load Balancing:** Proper configuration ensures an even distribution of packets, preventing any single queue or CPU core from becoming a bottleneck.
- **Scalability:** Helps in scaling network performance by utilizing multiple cores efficiently.
- **Performance:** Reduces latency and increases throughput by optimizing packet processing.

### Conclusion

Understanding and configuring `rx-flow-hash` fields is crucial for optimizing network performance, especially in high-speed networking environments. By selecting appropriate fields based on your network traffic patterns and requirements, you can ensure efficient load balancing and better utilization of hardware resources.

### Ofload
### Link
* [NIC Offloads](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/6/html/performance_tuning_guide/network-nic-offloads#network-nic-offloads)

The default Ethernet maximum transfer unit (MTU) is 1500 bytes, which is the largest frame size that can usually be transmitted. This can cause system resources to be underutilized, for example, if there are 3200 bytes of data for transmission, it would mean the generation of three smaller packets. There are several options, called offloads, which allow the relevant protocol stack to transmit packets that are larger than the normal MTU. Packets as large as the maximum allowable 64KiB can be created, with options for both transmitting (Tx) and receiving (Rx). When sending or receiving large amounts of data this can mean handling one large packet as opposed to multiple smaller ones for every 64KiB of data sent or received. This means there are fewer interrupt requests generated, less processing overhead is spent on splitting or combining traffic, and more opportunities for transmission, leading to an overall increase in throughput.


### Offload Types
#### TCP Segmentation Offload (TSO)
Uses the TCP protocol to send large packets. Uses the NIC to handle segmentation, and then adds the TCP, IP and data link layer protocol headers to each segment.

#### UDP Fragmentation Offload (UFO)
Uses the UDP protocol to send large packets. Uses the NIC to handle IP fragmentation into MTU sized packets for large UDP datagrams.

#### Generic Segmentation Offload (GSO)
Uses the TCP or UDP protocol to send large packets. If the NIC cannot handle segmentation/fragmentation, GSO performs the same operations, bypassing the NIC hardware. This is achieved by delaying segmentation until as late as possible, for example, when the packet is processed by the device driver.

#### Large Receive Offload (LRO)
Uses the TCP protocol. All incoming packets are re-segmented as they are received, reducing the number of segments the system has to process. They can be merged either in the driver or using the NIC. A problem with LRO is that it tends to resegment all incoming packets, often ignoring differences in headers and other information which can cause errors. It is generally not possible to use LRO when IP forwarding is enabled. LRO in combination with IP forwarding can lead to checksum errors. Forwarding is enabled if /proc/sys/net/ipv4/ip_forward is set to 1.

#### Generic Receive Offload (GRO)
Uses either the TCP or UDP protocols. GRO is more rigorous than LRO when resegmenting packets. For example it checks the MAC headers of each packet, which must match, only a limited number of TCP or IP headers can be different, and the TCP timestamps must match. Resegmenting can be handled by either the NIC or the GSO code.

#### Using NIC Offloads
Offloads should be used on high speed systems that transmit or receive large amounts of data and favor throughput over latency. Because using offloads greatly increases the capacity of the driver queue, latency can become an issue. An example of this would be a system transferring large amounts of data using large packet sizes, but is also running lots of interactive applications. Because interactive applications send small packets at timed intervals there is a very real risk that those packets may become 'trapped' in the buffer while larger packets in front of them are processed, causing unacceptable latency.
To check current offload settings use the ethtool command. Some device settings may be listed as fixed, meaning they cannot be changed.

Command syntax:
```
ethtool -k ethernet_device_name
```

Example 8.1. Check Current Offload Settings
```
$ ethtool -k em1
Features for em1:
rx-checksumming: on
tx-checksumming: on
tx-checksum-ipv4: off [fixed]
tx-checksum-ip-generic: on
tx-checksum-ipv6: off [fixed]
tx-checksum-fcoe-crc: off [fixed]
tx-checksum-sctp: off [fixed]
scatter-gather: on
tx-scatter-gather: on
tx-scatter-gather-fraglist: off [fixed]
tcp-segmentation-offload: on
tx-tcp-segmentation: on
tx-tcp-ecn-segmentation: off [fixed]
tx-tcp6-segmentation: on
udp-fragmentation-offload: off [fixed]
generic-segmentation-offload: on
generic-receive-offload: on
large-receive-offload: off [fixed]
rx-vlan-offload: on
tx-vlan-offload: on
ntuple-filters: off [fixed]
receive-hashing: on
highdma: on [fixed]
rx-vlan-filter: off [fixed]
vlan-challenged: off [fixed]
tx-lockless: off [fixed]
netns-local: off [fixed]
tx-gso-robust: off [fixed]
tx-fcoe-segmentation: off [fixed]
tx-gre-segmentation: off [fixed]
tx-ipip-segmentation: off [fixed]
tx-sit-segmentation: off [fixed]
tx-udp_tnl-segmentation: off [fixed]
tx-mpls-segmentation: off [fixed]
fcoe-mtu: off [fixed]
tx-nocache-copy: off
loopback: off [fixed]
rx-fcs: off
rx-all: off
tx-vlan-stag-hw-insert: off [fixed]
rx-vlan-stag-hw-parse: off [fixed]
rx-vlan-stag-filter: off [fixed]
l2-fwd-offload: off [fixed]
busy-poll: off [fixed]
```

In `ethtool`, the term "offload" refers to various network offloading features supported by network interface cards (NICs). These features allow certain network processing tasks to be offloaded from the CPU to the NIC, which can improve overall system performance by freeing up CPU resources and reducing latency. 

### Common Offload Features in `ethtool`

Here are some of the most common offload features that you can manage with `ethtool`:

#### 1. TCP Segmentation Offload (TSO)
TSO allows the NIC to handle the segmentation of large TCP packets into smaller ones that fit the MTU (Maximum Transmission Unit) of the network, reducing the CPU load associated with this task.

#### 2. Generic Segmentation Offload (GSO)
GSO is similar to TSO but works with various types of traffic, not just TCP. It allows the NIC to segment large packets from the host into smaller packets.

#### 3. Generic Receive Offload (GRO)
GRO enables the NIC to merge multiple incoming packets from the same TCP stream into larger buffers before passing them up the stack, reducing CPU usage and improving performance.

#### 4. Large Receive Offload (LRO)
LRO aggregates incoming packets into larger ones, reducing the number of packets the CPU needs to process. This is mostly used in high-performance network environments.

#### 5. Receive Side Scaling (RSS)
RSS allows the NIC to distribute incoming network traffic across multiple CPU cores, improving parallelism and performance on multi-core systems.

#### 6. Checksum Offload
Checksum offload allows the NIC to handle the computation and verification of checksums for TCP/UDP packets, offloading this task from the CPU.

### Using `ethtool` to Manage Offload Features

#### Display Current Offload Settings

To display the current offload settings for a network interface, you can use the following command:

```bash
ethtool -k <interface>
```

**Example:**

```bash
ethtool -k eth0
```

This command will display the offload settings for the `eth0` interface.

#### Enable or Disable Offload Features

To enable or disable a specific offload feature, you can use the `-K` option followed by the feature name and its desired state (`on` or `off`).

**Syntax:**

```bash
ethtool -K <interface> <feature> <state>
```

**Examples:**

- To enable TSO on `eth0`:

  ```bash
  ethtool -K eth0 tso on
  ```

- To disable GRO on `eth0`:

  ```bash
  ethtool -K eth0 gro off
  ```

### Conclusion
Understanding and managing offload features with `ethtool` can help optimize network performance by leveraging the capabilities of your NIC. By offloading tasks such as packet segmentation, checksum computation, and traffic distribution to the NIC, you can reduce CPU load and improve the efficiency and speed of your network operations.

* rx - receive (RX) checksumming
* tx - transmit (TX) checksumming
* sg - scatter-gather
* tso - TCP segmentation offload
* ufo - UDP fragmentation offload
* gso - generic segmentation offload
* gro - generic receive offload
* lro - large receive offload
* rxvlan - receive (RX) VLAN acceleration
* txvlan - transmit (TX) VLAN acceleration
* ntuple - receive (RX) ntuple filters and actions
* rxhash - receive hashing offload

## Command-Line Network Monitoring Tools
### Link
* [Best Tools to Monitor Network Bandwidth on a Linux Server](https://phoenixnap.com/kb/linux-network-bandwidth-monitor-traffic)
* [How to display network traffic in the terminal?](https://askubuntu.com/questions/257263/how-to-display-network-traffic-in-the-terminal)

### bmon - Bandwidth Monitor and Rate Estimator
bmon monitors bandwidth utilization, along with keeping a running rate estimate. It provides usage for each device individually, allowing users to track bandwidth across multiple network adapters.

bmon captures network statistics and provides a human-friendly output. Another positive feature is that the output includes a graph, providing bandwidth usage at a glance.

```
sudo apt install bmon
```

![](https://i.sstatic.net/WqOh6.png)


### vnStat - Network Traffic Monitor
vnStat works by running a daemon that captures and records bandwidth data. It reads data from the kernel to stay light on resource usage. The tool can run in real-time by specifying the -l option. The key feature of vnStat are persistent records - as the daemon runs, it collects and stores bandwidth usage logs.

The vnstat command can be used to display usage statistics, and it is best suited for statistical reporting. To install vnStat, run:
```
sudo apt install vnstat
```

![](https://phoenixnap.com/kb/wp-content/uploads/2022/12/vnstat-interface.png)

## dmesg
dmesg is a command on Linux systems, including Ubuntu, used to examine and manage the kernel ring buffer. This buffer stores messages related to the system's kernel activities, such as hardware initialization, driver messages, and system events. These messages are crucial for diagnosing and troubleshooting hardware and driver-related issues.

Here's an in-depth look at dmesg, including its usage, typical outputs, and common options:

### Overview of dmesg
Purpose: To display system messages that are typically logged by the kernel. This includes boot messages, hardware initialization, driver information, and errors.
Location: dmesg reads from the kernel ring buffer, which is also accessible at /var/log/dmesg.
Basic Usage
The simplest way to use dmesg is to run it without any arguments:

This outputs the entire kernel message buffer to the terminal. Given the large amount of information, it’s often useful to use tools like less to navigate through the output:
```
dmesg | less
```

Example Output:
```
[    0.000000] Initializing cgroup subsys cpuset
[    0.000000] Initializing cgroup subsys cpu
[    0.000000] Linux version 5.15.0-50-generic (buildd@lcy02-amd64-003) (gcc (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0, GNU ld (GNU Binutils for Ubuntu) 2.34) #55-Ubuntu SMP Tue Sep 13 19:47:35 UTC 2022 (Ubuntu 5.15.0-50.55-generic 5.15.39)
[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz-5.15.0-50-generic root=UUID=e6f1edc2-0c7f-4e1f-9c5a-dfcf6b96f40d ro quiet splash
...
```

### Filtering Messages by Keywords
You can search for specific messages using grep:
```
dmesg | grep <keyword>
```

Example: To find all messages related to the eth0 network interface:
```
dmesg | grep eth0
```

### Summary
dmesg is a powerful tool for viewing kernel messages in Linux, providing insights into hardware, drivers, and system events.
Typical Usage: Includes filtering messages, following live logs, and decoding timestamps and log levels.
Practical Applications: Useful for diagnosing hardware issues, driver problems, network troubles, and more.
Understanding and utilizing dmesg effectively can be crucial for system administrators and anyone involved in maintaining Linux systems. It provides a wealth of information directly from the kernel, making it an invaluable tool for troubleshooting and system analysis

The `ulimit -n` command in Unix-based systems, such as Linux, is used to display or set the maximum number of open file descriptors a process can have. This limit is important for applications that open many files or network connections simultaneously, such as web servers and database servers.

### Usage

- **Display current limit:**
  ```sh
  ulimit -n
  ```
  This command will print the current limit of open file descriptors for the shell session.

- **Set a new limit:**
  ```sh
  ulimit -n <new_limit>
  ```
  For example, to set the limit to 4096:
  ```sh
  ulimit -n 4096
  ```

### Types of Limits

- **Soft limit:** The value that the kernel enforces for the corresponding resource. This limit can be increased by a non-privileged user up to the hard limit.
- **Hard limit:** The ceiling for the soft limit. This limit can only be increased by the superuser (root).

### Example

To display the current limit:
```sh
ulimit -n
```

To set the limit to 4096:
```sh
ulimit -n 4096
```

### Persistent Changes

To make the changes persistent across reboots, you need to modify configuration files such as `/etc/security/limits.conf` or other relevant system-specific files.

For example, you can add the following lines to `/etc/security/limits.conf`:
```
*               soft    nofile          4096
*               hard    nofile          8192
```

Then, apply the changes by logging out and logging back in, or by restarting the system.

Understanding and properly configuring `ulimit -n` is crucial for ensuring that applications running on your system have the necessary resources to handle the required number of open files and connections.

## Syslog logging driver
* [logging syslog](https://docs.docker.com/config/containers/logging/syslog/)
* [logging configure](https://docs.docker.com/config/containers/logging/configure/)

Docker log drivers are mechanisms in Docker that handle the management, storage, and delivery of logs produced by running containers. Understanding Docker log drivers is crucial for efficiently handling logs, which are essential for debugging, monitoring, and maintaining containerized applications.

### What is a Docker Log Driver?

A Docker log driver defines how and where log data for a container is stored. Docker supports multiple log drivers, each designed for different logging requirements and environments. These drivers can send logs to various destinations, such as local files, remote servers, or centralized logging systems.

### Types of Docker Log Drivers

Docker supports several log drivers, including:

1. **json-file**: The default logging driver. Logs are stored as JSON in a file on the local disk.
2. **syslog**: Logs are sent to the syslog daemon.
3. **journald**: Logs are sent to the `journald` service.
4. **gelf**: Logs are sent to a Graylog Extended Log Format (GELF) endpoint.
5. **fluentd**: Logs are sent to a Fluentd endpoint.
6. **awslogs**: Logs are sent to Amazon CloudWatch.
7. **splunk**: Logs are sent to a Splunk endpoint.
8. **etwlogs**: Logs are sent to Windows Event Log (for Windows containers).
9. **none**: No logs are collected.

### Setting a Log Driver

You can set the log driver at two levels:
1. **Daemon Level**: Applies to all containers running on the Docker host.
2. **Container Level**: Applies only to a specific container.

#### Setting the Log Driver at the Daemon Level

To set the log driver for all containers, you need to modify the Docker daemon configuration file (`/etc/docker/daemon.json`) and add the following configuration:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

After updating the configuration, restart the Docker daemon:

```bash
sudo systemctl restart docker
```

#### Setting the Log Driver at the Container Level

You can specify the log driver when you run a container using the `--log-driver` option:

```bash
docker run --log-driver syslog alpine echo "Hello, Docker!"
```

Or you can use the `--log-opt` option to set specific logging options:

```bash
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3 alpine echo "Hello, Docker!"
```

### Example: Using Fluentd Log Driver

Fluentd is a popular open-source data collector that can handle log data from various sources. Let's set up a Docker container to use the Fluentd log driver.

1. **Install Fluentd**: Make sure you have Fluentd running. You can run it as a Docker container:

    ```bash
    docker run -d -p 24224:24224 -v /path/to/fluentd/config:/fluentd/etc fluent/fluentd:v1.11-1
    ```

2. **Configure Docker to Use Fluentd**:

    ```json
    {
      "log-driver": "fluentd",
      "log-opts": {
        "fluentd-address": "localhost:24224",
        "tag": "docker.{{.ID}}"
      }
    }
    ```

3. **Run a Container with Fluentd Logging**:

    ```bash
    docker run --log-driver=fluentd --log-opt fluentd-address=localhost:24224 alpine echo "Hello, Fluentd!"
    ```

### Viewing Logs

Depending on the log driver you use, logs can be viewed in different ways. For example:

- **json-file**: Logs are stored in the `/var/lib/docker/containers/<container-id>/` directory.
- **syslog**: Logs can be viewed using the `syslog` or `journalctl` commands.
- **fluentd**: Logs are collected and managed by Fluentd and can be viewed based on Fluentd's configuration.

### Summary
Docker log drivers provide flexible options for managing and storing container logs. By choosing the appropriate log driver and configuring it correctly, you can efficiently handle logs for your containerized applications, ensuring you have the necessary information for monitoring and troubleshooting.