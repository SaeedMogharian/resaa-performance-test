# RTPENGINE Test

## Two-way tests:

## Test 1: 1000 concurrent calls
`./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 20s -r 50 -rp 1s -m 2000`

## Test 2: 1200 concurrent calls
`./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 20s -r 60 -rp 1s -m 2000`

## Test 3: 1300 concurrent calls
`./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 20s -r 65 -rp 1s -m 3000`
## Test 4: 1500 concurrent calls
`./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 25s -r 60 -rp 1s -m 3000`

## Test 5: 1500 concurrent calls
` ./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 50s -r 30 -rp 1s -m 3000`

## Test 6: 2000 concurrent calls
` ./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 50s -r 40 -rp 1s -m 4000`

## Test 7: 3000 concurrent calls
` ./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 60s -r 50 -rp 1s -m 6000`

## Test 8: 4000 concurrent calls
` ./sipp -sf client.xml -inf p1.csv 192.168.21.45:5060 -p 6060 -mi 192.168.21.56 -mp 10000 -d 80s -r 50 -rp 1s -m 8000`
---> Not Happy!!!

