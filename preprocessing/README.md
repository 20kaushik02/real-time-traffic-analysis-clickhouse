# Data filtering, preprocessing and selection for further use

## Traffic data

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

## IP geolocation database

- This project uses the IP2Location LITE database for [IP geolocation](https://lite.ip2location.com)
- bit of preprocessing to leave out country code and convert IP address from decimal format to dotted string format

# Setting up Kafka
- Download and install kafka [from here](https://kafka.apache.org/downloads)
- Run all commands in separate terminals from installation location
- Zookeeper:
  - Windows: `.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties`
  - Mac: `bin/zookeeper-server-start.sh config/zookeeper.properties`
- Kafka Broker:
  - Windows: `.\bin\windows\kafka-server-start.bat .\config\server.properties`
  - Mac: `bin/kafka-server-start.sh config/server.properties`
- Creating a Kafka topic:
  - Windows: `.\bin\windows\kafka-topics.bat --create --topic %topicname% --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`
  - Mac: `bin/kafka-topics.sh --create --topic %topicname% --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`


# Streaming from pcap file using Kafka
- Start zookeeper and Kafka broker whenever python code is run after machine reboot
- Run pcap_processor.py file
- Arguments
  - -f or --pcap_file: pcap file path, mandatory argument
  - -o or --out_file: output csv file path
  - -x or --sample: boolean value indicating if data has to be sampled
  - -s or --stream: boolean value indicating if kafka streaming should happen
  - --stream_size: integer indicating number of sampled packets
  - -d or --debug: boolean value indicating if program is run in debug mode
  

python pcap_processor.py -f C:/Users/akash/storage/Asu/sem3/dds/project/202310081400.pcap -s --sample-size 1000
