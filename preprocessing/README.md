# Data filtering, preprocessing and selection for further use

- IP packet traces are taken [from here](https://mawi.wide.ad.jp/mawi/samplepoint-F/2023/), specifically from 2023/10/01-2023/10/31 (yet to confirm)
- Filtering - TODO
  - L4 - Limit to TCP and UDP
    - maybe GRE for VPN usage?
  - L3 - IPv6 is only around 10%, let's drop it
- Selection (of fields):
  - Timestamp - note: capture window is from 0500-0515 UTC
  - IP
    - addresses - src, dst
    - protocol - 6 (TCP) or 17 (UDP). cld go for boolean to save space
  - TCP
    - ports - sport, dport
  - Packet size - in bytes - could exclude L2?
