import struct
import socket
import csv

sample_size = 100
batch_size = 10000

sample = True


def int_to_ipv4(num: int) -> str:
    return socket.inet_ntoa(struct.pack("!L", num))


with open("IP2LOCATION-LITE-DB3.csv", "r") as input_file, open(
    "geoip.csv", "w", newline=""
) as output_file:
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)

    # header row
    writer.writerow(
        [
            "ip_from",
            "ip_to",
            "country",
            "region",
            "city",
        ]
    )

    records = []
    for idx, record in enumerate(reader):
        new_record = [
            int_to_ipv4(int(record[0])),
            int_to_ipv4(int(record[1])),
            record[3],
            record[4],
            record[5],
        ]
        records.append(new_record)
        if sample and idx > sample_size:
            break
        if idx > 0 and idx % batch_size == 0:
            writer.writerows(records)
            records = []

    if len(records) > 0:
        writer.writerows(records)
