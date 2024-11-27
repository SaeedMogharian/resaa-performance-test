SIP registration is a procedure in which SIP UEs initiate requests to the subscribed network through the CloudSE2980 for service authorization. The CloudSE2980 provides the following services for registered users:
- The CloudSE2980 binds a user's **current address** to user **identity information** so that the user is able to use basic services, including session initiation/receiving and subscription.
    After the user is registered successfully using an IMPU, the CloudSE2980 will consider that all the IMPUs in the same implicit registration set are registered.
- The CloudSE2980 is deployed at the edge of the IP network, serves as SIP signaling proxy, and supports Network Address Translation (NAT) traversal and topology hiding.



## Register Procedure

The **registration procedure** described here outlines how a User Equipment (UE) registers itself with the IMS (IP Multimedia Subsystem) network via the Session Border Controller (SBC) while handling NAT traversal and security authentication. Let’s break it down step-by-step:

---
![[fig_cn_82_06_0000701.png]]
### **Step 1: UE Sends REGISTER Request**

1. **Request Creation**:
    - The UE sends a `REGISTER` request to the SBC.
    - This request contains:
        - `Contact` header: Contains the UE’s private IP address and port.
        - `Request-URI`: Indicates the destination (e.g., `sip:huawei.com`).
        - `Authorization` header: Includes preliminary authentication details.
        - Example of a `REGISTER` request is shown with headers like `From`, `To`, `Via`, etc.
2. **Purpose**:
    - The `REGISTER` request tells the network that this UE wants to associate its IMPU (IP Multimedia Public Identity) with its contact address so it can send/receive calls/messages.

---

### **Step 2: NAT Device Processes the REGISTER Request**

1. **NAT Translation**:
    - The NAT device allocates a public IP address and port for the UE.
    - It replaces the private address (from `Contact` and `Via` headers) with the public address.
2. **Forwarding to SBC**:
    - The NAT forwards the modified `REGISTER` request to the SBC with updated source IP and port.

---

### **Step 3: SBC Processes the REGISTER Request**

1. **Core-Side Allocation**:
    - The SBC assigns a core-side signaling address and port for communication with the core network.
    - It modifies the `Contact` header to use the core-side signaling address.
2. **Forwarding to Core Network**:
    - The SBC forwards the updated `REGISTER` request to the UE’s core network.

---

### **Step 4: Core Network Responds with 401 Unauthorized**

1. **401 Unauthorized Response**:
    - The core network responds with a `401 Unauthorized` message.
    - This indicates that the SBC must authenticate itself with the core network.
2. **WWW-Authenticate Header**:
    - The `401 Unauthorized` message includes a `WWW-Authenticate` header with details like a `nonce` (a unique challenge for authentication).
3. **SBC Processes Response**:
    - The SBC updates the source and destination addresses in the `401 Unauthorized` response (replacing core-side signaling info with access-side info).
    - It forwards the response to the NAT, which then forwards it to the UE.

---

### **Step 5: UE Processes 401 Unauthorized**

1. **Authentication Handling**:
    - The UE authenticates the core network using the provided `nonce` and its local security credentials (keys).
    - If authentication is successful, the UE calculates a response (`RES`) and generates a new `REGISTER` request with this `RES`.
2. **New REGISTER Request**:
    - The UE sends the updated `REGISTER` request to the NAT, which forwards it to the SBC.

---

### **Step 6: SBC and Core Network Handle Updated REGISTER Request**

1. **SBC Processing**:
    - The SBC repeats its earlier steps:
        - Modifies the `Contact` header to use core-side signaling info.
        - Forwards the request to the core network.
2. **Core Network Validation**:
    - The core network authenticates the UE using the `RES`.
    - Upon successful authentication, it responds with a `200 OK` message.

---

### **Step 7: 200 OK Response**

1. **Core Network to SBC**:
    - The `200 OK` response indicates successful registration.
    - It includes:
        - `P-Associated-URI` (if supported): Lists associated URIs for the user.
        - `Contact` header: Confirms the registered address.
2. **SBC Processing**:
    - The SBC updates the `200 OK` response by:
        - Replacing core-side signaling info with access-side signaling info.
        - Replacing the `Contact` header with the UE’s public IP/port.
3. **Forwarding to UE**:
    - The SBC forwards the response to the NAT, which delivers it to the UE.

---

### **Step 8: Registration Complete**

1. **UE Can Send/Receive Calls**:
    - Once the `200 OK` is received, the UE is registered.
    - Based on the `P-Associated-URI` or `To` header, the SBC determines how the UE can make/receive calls:
        - With `P-Associated-URI`: Use the URIs listed there.
        - Without `P-Associated-URI`: Use URIs from the `To` header (SIP or TEL).
2. **Special Handling for Forking Users**:
    - If multiple UEs share the same number but different addresses, the SBC assigns separate ports for each UE to distinguish between them.

---

### **Key Concepts**

- **NAT Traversal**:
    - NAT devices replace private IPs with public IPs to allow external communication.
    - SBC ensures proper address translation for both core-side and access-side signaling.
- **Authentication**:
    - `401 Unauthorized` prompts the UE to prove its identity.
    - The `RES` in the second `REGISTER` request is derived from the nonce and UE’s secret key.
- **Contact Header**:
    - Tracks the UE’s address for routing calls/messages post-registration.
- **SBC Role**:
    - Acts as a bridge between the UE (access-side) and core network.
    - Handles signaling address allocation and forwards/adjusts messages as needed.

By following these steps, the UE can successfully register with the IMS network and start using its services.