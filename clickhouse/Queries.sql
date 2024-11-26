-- TABLE CREATION
CREATE TABLE traffic_records ON cluster_1S_2R
(
    time_stamp DateTime64(3, 'Japan') CODEC(Delta, ZSTD),
    protocol Enum('TCP' = 1, 'UDP' = 2),
    from_IP IPv4,
    to_IP IPv4,
    port UInt16 CODEC(ZSTD),
    INDEX port_idx port TYPE bloom_filter GRANULARITY 10
) ENGINE = ReplicatedMergeTree( '/clickhouse/tables/{shard}/traffic_records', '{replica}')
ORDER BY time_stamp
SETTINGS storage_policy = 'hot_cold'
TTL time_stamp + INTERVAL 5 DAY TO VOLUME 'cold_disk';

CREATE TABLE ip_region_map ON cluster_1S_2R
(
    ip_range_start IPv4,
    ip_range_end IPv4,
    region String,
    INDEX region_ind region TYPE bloom_filter
) ENGINE = ReplicatedMergeTree( '/clickhouse/tables/{shard}/ip_region_map', '{replica}')
ORDER BY ip_range_start;