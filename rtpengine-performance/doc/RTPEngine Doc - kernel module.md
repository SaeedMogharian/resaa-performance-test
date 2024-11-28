This documentation provides an overview of the `rtpengine`, specifically focusing on two core aspects: **userspace daemon** operation and **in-kernel packet forwarding**. The `rtpengine` is commonly used to forward RTP (Real-time Transport Protocol) packets, especially for Voice-over-IP (VoIP) services like SIP (Session Initiation Protocol).

Here’s a breakdown of the key points:

### Userspace Daemon
The **userspace daemon** (`rtpengine`) is responsible for handling the RTP packet forwarding. The user-configurable options and details can be found in the `rtpengine(1)` man page. In its normal operation, each packet that arrives needs to be processed by the daemon, resulting in performance overhead due to the many small packets RTP traffic uses. The overhead includes multiple context switches between the kernel and userspace, involving the kernel network stack, the daemon, and the RTP packet processing, all of which can be inefficient for high-rate traffic.

### In-Kernel Packet Forwarding
To alleviate the performance issues of userspace-only processing, `rtpengine` offers a **kernel module** that offloads most of the packet forwarding to kernel space, significantly reducing CPU usage and improving the system's capacity to handle more concurrent calls. The kernel module, called `xt_RTPENGINE`, integrates with **nftables**, allowing UDP traffic to be forwarded directly by the kernel rather than going through the userspace daemon.

#### Prerequisites:
1. **xt_RTPENGINE kernel module** must be loaded.
2. A **nftables rule** must be created to pass UDP packets to the kernel module.
3. The **rtpengine daemon** must be running to manage and communicate with the kernel module.

#### Workflow:
1. Initially, all RTP packets are handled in userspace.
2. Over time, after observing the traffic, the daemon will push forwarding rules to the kernel.
3. From then on, packets are forwarded entirely in-kernel, bypassing the userspace daemon and improving performance.
4. If in-kernel forwarding fails or is disabled, it falls back to userspace forwarding.

### Kernel Module Management
- The kernel module manages **forwarding tables**, identified by IDs. By default, up to 64 forwarding tables can be created.
- Each running instance of `rtpengine` manages one forwarding table, with the most common setup being a single daemon instance with ID 0.
- The module can be manually loaded using `modprobe xt_RTPENGINE` and inspected via `/proc/rtpengine/`.
- The **nftables rules** are created and managed by the daemon but can also be manually configured if needed.

### Example Commands:
- Load the kernel module: `modprobe xt_RTPENGINE`
- Manually create a forwarding table: `echo 'add 42' > /proc/rtpengine/control`
- Start the daemon: `/usr/bin/rtpengine --table=0 --interface=10.64.73.31`

### Summary:
This documentation outlines how to configure and operate `rtpengine` for high-performance RTP packet forwarding, leveraging both userspace and in-kernel operations. The key benefit of using in-kernel forwarding is the drastic reduction in overhead and improved system performance, especially under high load scenarios.