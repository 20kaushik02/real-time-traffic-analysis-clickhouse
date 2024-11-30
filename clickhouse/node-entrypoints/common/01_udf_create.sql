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

