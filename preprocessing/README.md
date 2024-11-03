# Data filtering, preprocessing and selection for further use

- IP packet traces are taken [from here](https://mawi.wide.ad.jp/mawi/samplepoint-F/2023/), specifically from 2023/10/01-2023/10/31 (yet to confirm)
- Filtering - TODO
  - L4 - Limit to TCP and UDP
    - maybe GRE for VPN usage?
  - L3 - IPv6 is only around 10%, let's drop it
- Selection (of fields):
  - Timestamp
    - capture window is from 0500-0515 UTC
    - nanosecond precision, use DateTime64 data type in ClickHouse
  - IP
    - addresses - src, dst
    - protocol - TCP or UDP. cld go for boolean in ClickHouse to save space
  - TCP/UDP
    - ports - sport, dport
  - Packet size - in bytes
