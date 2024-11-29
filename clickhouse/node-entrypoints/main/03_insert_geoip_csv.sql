INSERT INTO ip_region_map
FROM INFILE '/tmp/seedData/csv/ip_region_map.csv'
FORMAT CSVWithNames;