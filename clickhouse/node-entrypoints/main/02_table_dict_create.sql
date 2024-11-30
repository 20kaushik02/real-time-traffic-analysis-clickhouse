-- local table creation
CREATE TABLE traffic_records (
	time_stamp DateTime64 (6, 'Japan') CODEC (Delta, ZSTD),
	l4_protocol Enum8 ('TCP' = 1, 'UDP' = 2),
	src_ip IPv4,
	dst_ip IPv4,
	src_port UInt16 CODEC (ZSTD),
	dst_port UInt16 CODEC (ZSTD),
	pkt_len UInt16 CODEC (ZSTD),
	INDEX port_idx src_port TYPE bloom_filter GRANULARITY 10
) ENGINE = ReplicatedMergeTree(
	'/clickhouse/tables/{shard}/traffic_records',
	'{replica}'
)
ORDER BY time_stamp
TTL toDateTime(time_stamp) + INTERVAL 410 DAY TO VOLUME 'cold_vol' -- october 15
SETTINGS storage_policy = 'hot_cold';

CREATE TABLE ip_region_map (
	ip_range_start IPv4,
	ip_range_end IPv4,	
	region LowCardinality(String),
	ip_range_cidr String MATERIALIZED IPv4RangeToCIDRString(ip_range_start, ip_range_end),
	INDEX region_idx region TYPE bloom_filter
) ENGINE = ReplicatedMergeTree(
	'/clickhouse/tables/{shard}/ip_region_map',
	'{replica}'
)
ORDER BY ip_range_start;

CREATE DICTIONARY ip_region_dict
(ip_range_cidr String, region String)
PRIMARY KEY ip_range_cidr
SOURCE(CLICKHOUSE(TABLE 'ip_region_map'))
LAYOUT(ip_trie)
LIFETIME(3600);
