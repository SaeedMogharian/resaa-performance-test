# SIPp IMS Registration Scenario

This guide explains how to use the `register.xml` scenario for testing SIP registration procedures in an IMS network using SIPp. The scenario simulates the full registration process, including handling authentication challenges and receiving successful registration responses.

## Scenario Flow

The IMS registration process follows this flow:

1. **Initial REGISTER Request**
2. **Handling the 401 Unauthorized Challenge**
3. **Authenticated REGISTER Request**
4. **Successful Registration Response (200 OK)**

---

## Detailed Breakdown of `register.xml`

### 1. **Initial REGISTER Request**

The scenario begins by sending a `REGISTER` request to the IMS network. It contains essential fields such as the destination server, local IP, port, and contact information.

```xml
<send>
  <![CDATA[
  REGISTER sip:[field1] SIP/2.0
  Via: SIP/2.0/[transport] [local_ip]:[local_port];rport;branch=[branch]
  Route: <sip:[field2];lr>
  Max-Forwards: 70
  From: <sip:[field0]@[field1]>;tag=[call_number]
  To: <sip:[field0]@[field1]>
  Call-ID: [call_id]
  CSeq: 1 REGISTER
  Contact: <sip:[field0]@[local_ip]:[local_port];transport=[transport]>
  Expires: 3600
  Allow: PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, INFO, SUBSCRIBE, NOTIFY, REFER, MESSAGE, OPTIONS
  Content-Length:  0
  ]]>
</send>
```

- **[field1]**: The IMS domain or SIP server to register with.
- **[field0]**: The user identifier (e.g., username).

### 2. **Expect 100 Trying Response**

The server responds with a `100 Trying` message, which indicates that the request is being processed. SIPp waits for this acknowledgment before moving on.

```xml
<recv response="100">
</recv>
```

### 3. **Expect 401 Unauthorized Response (Authentication Challenge)**

The server will return a `401 Unauthorized` response if authentication is required. This indicates that the client must provide credentials in the subsequent REGISTER request.

```xml
<recv response="401" auth="true">
</recv>
```

- The `auth="true"` attribute tells SIPp to handle the authentication challenge automatically.

### 4. **Send REGISTER Request with Authentication**

After receiving the `401 Unauthorized` response, the next step is to send a second `REGISTER` request, this time including the `Authorization` header with the necessary authentication credentials (username, password, and other parameters).

```xml
<send>
  <![CDATA[
  REGISTER sip:[field1] SIP/2.0
  Via: SIP/2.0/[transport] [local_ip]:[local_port];rport;branch=[branch]
  Route: <sip:[field2];lr>
  Max-Forwards: 70
  From: <sip:[field0]@[field1]>;tag=[call_number]
  To: <sip:[field0]@[field1]>
  Call-ID: [call_id]
  CSeq: 2 REGISTER
  Contact: <sip:[field0]@[local_ip]:[local_port];transport=[transport]>
  Expires: 3600  
  [field3] <!-- Authentication header is added here -->
  Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO
  Supported: path
  Content-Length: 0
  ]]>
</send>
```

- **[field3]**: The authentication header. This contains the credentials required by the server, including the digest authentication (username, realm, response, nonce, etc.).

The server expects this request with valid credentials, including a computed response to the server's `401` challenge.

### 5. **Expect 100 Trying Response**

The server will again respond with a `100 Trying` message, indicating the request is being processed.

```xml
<recv response="100">
</recv>
```

### 6. **Expect 200 OK Response (Registration Successful)**

Finally, if the authentication is correct, the server will respond with a `200 OK` message, indicating that the registration was successful.

```xml
<recv response="200">
  <action>
    <!-- Registration successful -->
    <log message="Registration successful for user [field0]@[local_ip]:[local_port]"/>
  </action>
</recv>
```

- The action inside the `<recv>` block logs the success message, confirming the registration.

---

## How to Run the Scenario

To run the registration test using SIPp, use the following command in the directory where SIPp is installed:

```bash
./sipp -sf register.xml -inf users.csv -p [local_port] [remote_ip] -m [test_count]
```

Where:

- **`[local_port]`**: The local port for SIP communication.
- **`[remote_ip]`**: The IP address of the IMS network or SIP server.
- **`[test_count]`**: The number of test iterations to run.

Scenario files:

- `register.xml`: The registration scenario.
- `reregister.xml`: A scenario for re-registering (with authentication included in the first request).
- `deregister.xml`: A scenario for de-registering (with authentication included in the first request and sets `expires=0`).

---

## CSV File for User Data (`users.csv`)

The `users.csv` file contains user data and authentication information. It follows the format below:

```csv
SEQUENTIAL
username1;sip_server1;sip_proxy1;[authentication username=username1 password=password1]
username2;sip_server2;sip_proxy2;[authentication username=username2 password=password2]
```

Where:

- `username1`: The SIP username for the first user.
- `sip_server1: The domain of the SIP server for the first user.
- `sip_proxy1`: The domain of the SIP proxy for the first user.
- `[authentication username=username1 password=password1]`: The authentication credentials for the first user.

---

## Troubleshooting

1. **401 Unauthorized Error**: If you receive a `401 Unauthorized` response, ensure that the authentication credentials in `register.xml` are correctly set and match the credentials provided in the `users.csv` file.
2. **200 OK Not Received**: If you don't receive a `200 OK` response, check that the authentication process was successful. Verify that the `Authorization` header in the second `REGISTER` request is formatted correctly.
3. **Timeouts or Connection Issues**: Verify the SIP server's availability and ensure that the network connection is not being blocked by firewalls or other network restrictions.