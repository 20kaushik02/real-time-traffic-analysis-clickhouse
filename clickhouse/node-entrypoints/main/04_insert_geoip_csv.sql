INSERT INTO ip_region_map (ip_range_start, ip_range_end, country_code, country)
FROM INFILE '/var/lib/clickhouse/user_files/csv/ip_region_cc_map.csv'
FORMAT CSVWithNames;
