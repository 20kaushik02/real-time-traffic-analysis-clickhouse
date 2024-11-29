CREATE TABLE traffic_records_all
AS traffic_records
ENGINE = Distributed ('{cluster}', 'default', 'traffic_records');
