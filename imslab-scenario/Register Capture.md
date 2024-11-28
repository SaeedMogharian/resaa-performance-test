# Register

Session Initiation Protocol (REGISTER)
    Request-Line: REGISTER sip:ims.mnc011.mcc432.3gppnetwork.org SIP/2.0
    Message Header
        Via: SIP/2.0/UDP 192.168.20.86:62534;rport;branch=z9hG4bKPjfb8765652e99468592d8fb9cb7a778ee
        Route: <sip:pcscf.ims.mnc011.mcc432.3gppnetwork.org;lr>
        Max-Forwards: 70
        From: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>;tag=20449c5f331b40df9ef397f36718ec25
        To: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>
        Call-ID: 25536ca319b24a59835915a2ee246ef7
        [Generated Call-ID: 25536ca319b24a59835915a2ee246ef7]
        CSeq: 43598 REGISTER
        User-Agent: MicroSIP/3.21.5
        Contact: <sip:432011123456791@192.168.20.86:62534;ob>
        Expires: 300
        Allow: PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, INFO, SUBSCRIBE, NOTIFY, REFER, MESSAGE, OPTIONS
        Content-Length:  0
# 100 trying
# 401
Session Initiation Protocol (401)
    Status-Line: SIP/2.0 401 Unauthorized - Challenging the UE
    Message Header
        Via: SIP/2.0/UDP 192.168.20.86:62534;received=192.168.20.86;rport=62534;branch=z9hG4bKPjfb8765652e99468592d8fb9cb7a778ee
        From: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>;tag=20449c5f331b40df9ef397f36718ec25
        To: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>;tag=40604f13b94a047cd5bfb6f052bd927a-c9dd0000
        Call-ID: 25536ca319b24a59835915a2ee246ef7
        [Generated Call-ID: 25536ca319b24a59835915a2ee246ef7]
        CSeq: 43598 REGISTER
        WWW-Authenticate: Digest realm="ims.mnc011.mcc432.3gppnetwork.org", nonce="9141ed3a3de48a878ba1467f9cfa0a88", algorithm=MD5, qop="auth"
        Path: <sip:term@pcscf.ims.mnc011.mcc432.3gppnetwork.org;lr>
        Server: Kamailio S-CSCF
        Content-Length: 0
# register again with auth:
Session Initiation Protocol (REGISTER)
    Request-Line: REGISTER sip:ims.mnc011.mcc432.3gppnetwork.org SIP/2.0
    Message Header
        Via: SIP/2.0/UDP 192.168.20.86:62534;rport;branch=z9hG4bKPj310fdff2a21b4a7fa47ee2a0ce16e8ab
        Route: <sip:pcscf.ims.mnc011.mcc432.3gppnetwork.org;lr>
        Max-Forwards: 70
        From: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>;tag=20449c5f331b40df9ef397f36718ec25
        To: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>
        Call-ID: 25536ca319b24a59835915a2ee246ef7
        [Generated Call-ID: 25536ca319b24a59835915a2ee246ef7]
        CSeq: 43599 REGISTER
        User-Agent: MicroSIP/3.21.5
        Contact: <sip:432011123456791@192.168.20.86:62534;ob>
        Expires: 300
        Allow: PRACK, INVITE, ACK, BYE, CANCEL, UPDATE, INFO, SUBSCRIBE, NOTIFY, REFER, MESSAGE, OPTIONS
         […]Authorization: Digest username="432011123456791", realm="ims.mnc011.mcc432.3gppnetwork.org", nonce="9141ed3a3de48a878ba1467f9cfa0a88", uri="sip:ims.mnc011.mcc432.3gppnetwork.org", response="1038f0a088f300476ffffef5474a2c96", algorith
            Authentication Scheme: Digest
            Username: "432011123456791"
            Realm: "ims.mnc011.mcc432.3gppnetwork.org"
            Nonce Value: "9141ed3a3de48a878ba1467f9cfa0a88"
            Authentication URI: "sip:ims.mnc011.mcc432.3gppnetwork.org"
            Digest Authentication Response: "1038f0a088f300476ffffef5474a2c96"
            Algorithm: MD5
            CNonce Value: "47d4310d6e964d93b723b70941dd05a2"
            QOP: auth
            Nonce Count: 00000001
        Content-Length:  0


# 100 trying
# 200ok
Session Initiation Protocol (200)
    Status-Line: SIP/2.0 200 OK
    Message Header
        Via: SIP/2.0/UDP 192.168.20.86:62534;received=192.168.20.86;rport=62534;branch=z9hG4bKPj310fdff2a21b4a7fa47ee2a0ce16e8ab
        From: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>;tag=20449c5f331b40df9ef397f36718ec25
        To: <sip:432011123456791@ims.mnc011.mcc432.3gppnetwork.org>;tag=40604f13b94a047cd5bfb6f052bd927a-41e9fd69
        Call-ID: 25536ca319b24a59835915a2ee246ef7
        [Generated Call-ID: 25536ca319b24a59835915a2ee246ef7]
        CSeq: 43599 REGISTER
        Contact: <sip:432011123456791@192.168.20.26:62980;alias=192.168.20.26~62980~1;ob>;expires=192, <sip:432011123456791@192.168.20.86:62534;alias=192.168.20.86~62534~1;ob>;expires=270
        Path: <sip:term@pcscf.ims.mnc011.mcc432.3gppnetwork.org;lr>
        P-Associated-URI: <sip:98098765432100@ims.mnc011.mcc432.3gppnetwork.org>, <tel:98098765432100>
        Service-Route: <sip:orig@scscf.ims.mnc011.mcc432.3gppnetwork.org:6060;lr>
        Server: Kamailio S-CSCF
        Content-Length: 0
