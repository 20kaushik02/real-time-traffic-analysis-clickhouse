
# Kafka - Clickhouse Integration Testing  

## Execution Steps  

Ensure to pull the ClickHouse Docker image:  
```bash
docker-compose up -d
```  
Identify the custom networks created:  
```bash
docker network ls
```  
Inspect the keeper network and verify whether all the containers are connected to it:  
```bash
docker network inspect dds_proj_clickhouse-keeper-network
```  
If all the containers are not connected:  
```bash
docker-compose restart
```  
To execute queries:  
```bash
docker exec -it clickhouse-server1 clickhouse-client
```  
```bash
docker exec -it clickhouse-server2 clickhouse-client
```  

## Building Kafka Image  

Navigate to `/preprocessing` from the repo main directory:  
```bash
docker build -t <imagename>:latest -f Dockerfile.python .
```  
Tag the image:  
```bash
docker tag <imagename>:latest <dockerhub_id>/<imagename>:latest
```  
Push the image to Docker Hub:  
```bash
docker push <dockerhub_id>/<imagename>:latest
```  

## Testing the Integration  

Changes to make in `docker-compose.yml`:  
- `pcap_streamer => volumes`: `<local path where .pcap file is stored; don't change /data/pcap after : symbol>`  
- `pcap_streamer => image`: `<dockerhub_id>/<imagename>:latest`  

Navigate to `/clickhouse` from the repo main directory:  
```bash
docker stack deploy -c docker-compose.yml <stackname> --detach=false
```  
Check running services:  
```bash
docker service ls
```  
Check logs of the service:  
```bash
docker service logs <servicename>
```  

Get the container ID for the ClickHouse client:  
```bash
docker ps
```  
Check if the topic has all streamed data:  
```bash
docker exec -it clickhouse-kafka-1 kafka-console-consumer --bootstrap-server kafka:9092 --topic pcap_stream_new --from-beginning
```  
- Change the topic name if applicable.  
- The output should display all JSON packets.  

Get into the ClickHouse client:  
```bash
docker exec -it <server1's container ID from docker ps> clickhouse-client
```  
Check if tables are available:  
```bash
SHOW TABLES;
```  

If tables are not available, create the following:  

Create a table for `packets_data`:  
```sql
CREATE TABLE packets_data
(
    time Float64,
    l4_proto String,
    src_addr String,
    dst_addr String,
    src_port UInt16,
    dst_port UInt16,
    pkt_len UInt32
) ENGINE = MergeTree
ORDER BY time;
```  

Create a table for `kafka_stream`:  
```sql
CREATE TABLE kafka_stream
(
    time Float64,
    l4_proto String,
    src_addr String,
    dst_addr String,
    src_port UInt16,
    dst_port UInt16,
    pkt_len UInt32
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:9092',
         kafka_topic_list = 'pcap_stream_new',
         kafka_group_name = 'clickhouse_consumer',
         kafka_format = 'JSONEachRow',
         kafka_num_consumers = 1;
```  

Create a materialized view `kafka_to_packets`:  
```sql
CREATE MATERIALIZED VIEW kafka_to_packets
TO packets_data AS
SELECT
    time,
    l4_proto,
    src_addr,
    dst_addr,
    src_port,
    dst_port,
    pkt_len
FROM kafka_stream;
```  

Check table contents to verify data availability:  
```bash
SELECT * FROM packets_data LIMIT 10;
```  
```bash
SELECT COUNT(*) AS total_count_of_packets_streamed FROM packets_data;
```  
