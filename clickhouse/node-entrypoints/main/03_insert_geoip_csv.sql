INSERT INTO ip_region_map
FROM INFILE '/var/lib/clickhouse/user_files/csv/ip_region_map.csv'
FORMAT CSVWithNames;

-- https://clickhouse.com/blog/geolocating-ips-in-clickhouse-and-grafana#using-bit-functions-to-convert-ip-ranges-to-cidr-notation

CREATE FUNCTION unmatchedBits AS (ip_s, ip_e) -> if(
	bitXor(ip_s, ip_e) != 0,
	ceil(log2(bitXor(ip_s, ip_e))), 0
);

CREATE FUNCTION cidrSuffix AS (ip_s, ip_e) -> 32 - unmatchedBits(ip_s, ip_e);

CREATE FUNCTION cidrAddress AS (ip_s, ip_e) -> toIPv4(
	bitAnd(
		bitNot(pow(2, unmatchedBits(ip_s, ip_e)) - 1),
		ip_s
	)::UInt64
);

CREATE FUNCTION IPv4RangeToCIDRString AS (ip_s, ip_e) -> CONCAT(
	toString(cidrAddress(ip_s, ip_e)),
	'/',
	toString(cidrSuffix(ip_s, ip_e))
);

ALTER TABLE ip_region_map
ADD COLUMN ip_range_cidr String
MATERIALIZED IPv4RangeToCIDRString(ip_range_start, ip_range_end);

CREATE DICTIONARY ip_region_dict (ip_range_cidr String, region String) PRIMARY KEY ip_range_cidr SOURCE(CLICKHOUSE(TABLE 'ip_region_map')) LAYOUT(ip_trie) LIFETIME(3600);

-- SELECT
--     *,
--     dictGet('ip_region_dict', 'region', tuple(src_ip)) AS region
-- FROM traffic_records_all
-- LIMIT 10