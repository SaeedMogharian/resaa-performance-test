documentaion:
https://wiki.nftables.org/wiki-nftables/index.php/Configuring_tables
https://wiki.nftables.org/wiki-nftables/index.php/Simple_rule_management


When you set up RTPengine in kernel mode, it interacts with the kernel's packet filtering framework to handle media streams directly at the packet level, improving performance and reducing latency. The tables under `/proc/rtpengine` represent active RTP sessions, which are managed by the RTPengine kernel module. These tables track RTP streams for relaying media between different endpoints.

Here's a breakdown of how this works:

### 1. RTPengine Kernel Mode and `/proc/rtpengine`
In kernel mode, RTPengine hooks into the kernel's packet handling by leveraging the `nf_tables` (Netfilter tables), which is part of the Linux networking stack responsible for packet filtering, mangling, and routing.

- The `/proc/rtpengine/l0/list` is a virtual file provided by the RTPengine module. It lists the RTP sessions and their associated metadata, like IP addresses and ports.
- These entries are created dynamically when RTPengine is handling an RTP session. The kernel module inspects incoming and outgoing packets and forwards them according to the session rules.

### 2. Where Are the Rules That Match the Table?
The rules that match and forward RTP packets are injected into the kernel via `nftables`, which is the successor to `iptables`. When RTPengine is initialized, it sets up its own set of rules to capture and forward packets related to the RTP streams.

You can see the rules set up by RTPengine using `nft list ruleset` or `iptables -L`, depending on how it was set up.

### 3. Manually Creating a Table and Adding a Rule
If you want to manually create a similar table and add rules to `nftables` for packet forwarding, follow these steps:

#### Step 1: Create a New Table
Create a new table in `nftables` that will hold your rules. For instance, you can create a table for handling RTP traffic:

```bash
sudo nft add table inet rtp_table
```

#### Step 2: Add a Chain to the Table
Once the table is created, you need to add chains. A chain is a set of rules that define how packets will be handled (e.g., forwarded, dropped). For example:

```bash
sudo nft add chain inet rtp_table rtp_chain { type filter hook prerouting priority 0\; }
```

This chain is attached to the prerouting hook, which means it processes packets as they arrive at the network interface.

#### Step 3: Add Rules to the Chain
Now that the table and chain are ready, you can add rules that match specific RTP traffic and forward it. For example, to forward RTP packets from a specific IP address and port:

```bash
sudo nft add rule inet rtp_table rtp_chain ip saddr 192.168.1.10 udp dport 10000-20000 counter accept
```

This rule forwards UDP packets from the source IP `192.168.1.10` and destination ports between `10000` and `20000`, which are typically used for RTP traffic.

You can add more complex rules to match various RTP streams based on IPs, ports, protocols, etc.

#### Step 4: Verify the Rules
To check the rules you’ve added, use:

```bash
sudo nft list table inet rtp_table
```

#### Step 5: Set Up Packet Forwarding
If you want to forward packets between interfaces, you can set up additional rules. For example, to forward traffic from one interface to another:

```bash
sudo nft add rule inet rtp_table rtp_chain ip saddr 192.168.1.10 udp dport 10000-20000 counter dnat to 10.10.10.10:10000
```

This rule changes the destination of packets and forwards them to `10.10.10.10:10000`.

### 4. Integration with RTPengine
RTPengine will typically manage its own set of `nftables` rules dynamically as sessions are created and torn down. The entries you see under `/proc/rtpengine` represent active sessions managed by these rules. You can customize these by integrating your manually created tables or modifying RTPengine’s `nftables` setup if you need more control over packet flows.

Let me know if you need further details or specific examples for your setup!