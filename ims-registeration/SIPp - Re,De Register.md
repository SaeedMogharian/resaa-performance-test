Here are XML scenarios for **IMS Re-Register** and **De-Register** flows using SIPp. These scenarios follow a similar structure to the IMS registration flow you provided:

---

### IMS Re-Register Scenario

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- IMS Re-Registration Scenario -->
<scenario name="IMS Re-Registration">

  <!-- Send REGISTER Request with Updated Expiry -->
  <send>
    <![CDATA[
    REGISTER sip:[remote_ip]:[remote_port] SIP/2.0
    Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
    Max-Forwards: 70
    From: <sip:[field0]@[local_ip]:[local_port]>;tag=[call_number]
    To: <sip:[field0]@[local_ip]:[local_port]>
    Call-ID: [call_id]
    CSeq: [cseq] REGISTER
    Contact: <sip:[field0]@[local_ip]:[local_port];transport=[transport]>;expires=3600
    Authorization: Digest username="[field0]@[local_ip]:[local_port]", realm="[local_ip]:[local_port]", nonce="[$1]", uri="sip:[local_ip]:[local_port]"
    Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO
    Supported: path
    Content-Length: 0

    ]]>
  </send>

  <!-- Expect 200 OK Response -->
  <recv response="200" optional="false">
    <action>
      <!-- Re-Registration successful -->
      <log message="Re-Registration successful for user [field0]@[local_ip]:[local_port]"/>
    </action>
  </recv>

</scenario>
```

**Explanation:**

1. **Re-REGISTER Request:**
    
    - A `REGISTER` request is sent with an updated `expires` value to renew the registration.
    - The `Authorization` header includes the credentials from the initial registration.
    - Ensure the `CSeq` value is incremented for each subsequent `REGISTER` request.
2. **Expecting 200 OK Response:**
    
    - The scenario expects a `200 OK` response to confirm the successful re-registration.

---

### IMS De-Register Scenario

```xml
<?xml version="1.0" encoding="ISO-8859-1"?>
<!-- IMS De-Registration Scenario -->
<scenario name="IMS De-Registration">

  <!-- Send REGISTER Request with Expiry 0 -->
  <send>
    <![CDATA[
    REGISTER sip:[remote_ip]:[remote_port] SIP/2.0
    Via: SIP/2.0/[transport] [local_ip]:[local_port];branch=[branch]
    Max-Forwards: 70
    From: <sip:[field0]@[local_ip]:[local_port]>;tag=[call_number]
    To: <sip:[field0]@[local_ip]:[local_port]>
    Call-ID: [call_id]
    CSeq: [cseq] REGISTER
    Contact: <sip:[field0]@[local_ip]:[local_port];transport=[transport]>;expires=0
    Authorization: Digest username="[field0]@[local_ip]:[local_port]", realm="[local_ip]:[local_port]", nonce="[$1]", uri="sip:[local_ip]:[local_port]"
    Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO
    Supported: path
    Content-Length: 0

    ]]>
  </send>

  <!-- Expect 200 OK Response -->
  <recv response="200" optional="false">
    <action>
      <!-- De-Registration successful -->
      <log message="De-Registration successful for user [field0]@[local_ip]:[local_port]"/>
    </action>
  </recv>

</scenario>
```

**Explanation:**

1. **De-REGISTER Request:**
    
    - A `REGISTER` request is sent with the `expires` parameter set to `0` to indicate de-registration.
    - The `Authorization` header ensures that the request is authenticated.
2. **Expecting 200 OK Response:**
    
    - A `200 OK` response confirms that the user has been successfully de-registered from the IMS network.

---

### Notes for Both Scenarios:

- **Authentication Parameters:**
    
    - Ensure the `nonce`, `realm`, and `auth_response` values are correctly computed and reused from the initial registration.
- **Dynamic Placeholders:**
    
    - Replace placeholders (`[remote_ip]`, `[local_ip]`, etc.) dynamically with appropriate values during execution.
- **CSeq Handling:**
    
    - The `CSeq` value must increase with each subsequent `REGISTER` request, as per the SIP protocol requirements.
- **Execution Command:**
    
    - Use SIPp to execute the scenarios:
        
        ```
        sipp -sf ims_reregister.xml -inf users.csv -s [remote_ip] -p [local_port] -t [transport]
        sipp -sf ims_deregister.xml -inf users.csv -s [remote_ip] -p [local_port] -t [transport]
        ```
        
- **CSV File for User Data:**
    
    - Use the same CSV file format as in the registration scenario to provide user-specific data.

These scenarios can be used to simulate re-registration and de-registration flows in an IMS network while maintaining compliance with SIP and IMS standards.