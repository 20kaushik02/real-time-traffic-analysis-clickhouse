# Data filtering, preprocessing and selection for further use

- IP packet traces are taken [from here](https://mawi.wide.ad.jp/mawi/samplepoint-F/2023/)
- Filtering
  - L4 - Limit to TCP and UDP
  - L3 - IPv6 is only around 10%, let's drop it
- Selection of fields:
  - Timestamp
    - capture window is from 0500-0515 UTC
    - nanosecond precision, use `DateTime64` data type in ClickHouse
  - IP
    - addresses - src, dst
    - L4 protocol - TCP, UDP. use `Enum` data type in ClickHouse
  - TCP/UDP - ports - sport, dport
  - Packet size - in bytes
- `sample_output.csv` contains a partial subset of `202310081400.pcap`, ~600K packets
