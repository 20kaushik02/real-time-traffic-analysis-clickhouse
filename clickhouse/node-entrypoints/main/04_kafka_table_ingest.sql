CREATE TABLE traffic_records_kafka_queue (
	time Float64,
	l4_proto String,
	src_addr String,
	dst_addr String,
	src_port UInt16,
	dst_port UInt16,
	pkt_len UInt32
) ENGINE = Kafka() SETTINGS kafka_broker_list = 'kafka:9092',
kafka_topic_list = 'traffic_records_stream',
kafka_group_name = 'clickhouse_consumer',
kafka_format = 'JSONEachRow',
kafka_num_consumers = 1;

CREATE MATERIALIZED VIEW traffic_records_kafka_view TO traffic_records_all AS
SELECT time AS time_stamp,
	l4_proto AS l4_protocol,
	src_addr AS src_ip,
	dst_addr AS dst_ip,
	src_port,
	dst_port,
	pkt_len
FROM traffic_records_kafka_queue;
