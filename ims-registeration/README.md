SIPp Auth
https://sipp.readthedocs.io/en/v3.6.1/scenarios/sipauth.html



Test Framework:
https://blog.opensips.org/2023/04/04/sipssert-an-opensips-testing-framework/
https://github.com/OpenSIPS/SIPssert


##  Register Procedure Explanation:
1. **Initial REGISTER Request:**
    - The scenario begins by sending a `REGISTER` request to the IMS network.
2. **Handling 401 Unauthorized Response:**
    - The scenario expects a `401 Unauthorized` response, which indicates that the server requires authentication.
    - using` auth="true"` in the 401 receive header. SIPp acknowledge the authentication challenge/
3. **Authenticated REGISTER Request:**
    - A second `REGISTER` request is sent, this time including the `Authorization` header with the necessary credentials.
    - using `[athentication username="" password=""]`
4. **Expecting 200 OK Response:**
    - The scenario then waits for a `200 OK` response, indicating that the registration was successful.
### re-register and de-register:
- re-register is the same but it has the auth on the first request and it do the process from the 3th step.
- de-register similar to re-register start from the 3rd step with the auth already provided but it sets `expire=0` 

## Running the scenarios
- on a directory where SIPp is compiled
- `./sipp -sf register.xml -inf users.csv -p [local_port] [remote_ip] -m [test_count]`
- Replace `[remote_ip]`, `[local_port]`, and `[test_count]` with appropriate values.
- Scenario file could be `register.xml`, `reregister.xml`, `deregister.xml`

### CSV File for User Data `users.csv`:
``` 
SEQUENTIAL
username1;sip_server(domain)1;sip_proxy1;[authentication username=username1 password=password1]
username2;sip_server(domain)2;sip_proxy2;[authentication username=username2 password=password2]
```
