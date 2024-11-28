from argparse import ArgumentParser
from datetime import datetime, timezone
import csv

from scapy.packet import Packet
from scapy.utils import PcapReader
from scapy.layers.inet import IP, TCP, UDP

from kafka import KafkaProducer, KafkaConsumer
import json

dbg_print = lambda *x: DEBUG and print(f"[DEBUG] {x}")


# Kafka Configuration
KAFKA_TOPIC = "traffic_records_stream"
KAFKA_SERVER = "kafka:9092"  # Adjust to your Kafka server


class KafkaClient:
    def __init__(self, topic_name=None, mode="producer"):
        self.mode = mode
        self.topic_name = topic_name
        if mode == "producer":
            self.client = KafkaProducer(
                bootstrap_servers=[KAFKA_SERVER],
                max_request_size=200000000,
                # api_version=(0,11,5),
                value_serializer=lambda x: json.dumps(x).encode("utf-8"),
            )
        elif mode == "consumer" and topic_name is not None:
            self.client = KafkaConsumer(
                topic_name,
                bootstrap_servers=["localhost:9092"],
                api_version=(0, 11, 5),
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            )
        else:
            raise ValueError("Consumer mode requires a topic_name")


producer = KafkaClient(topic_name=KAFKA_TOPIC)


def pkt_filter(pkt: Packet) -> bool:
    """filter to include/exclude a packet"""
    try:
        assert IP in pkt
        assert pkt[IP].version == 4
        assert (TCP in pkt) or (UDP in pkt)
        return True
    except AssertionError:
        return False


def pkt_extract(pkt: Packet) -> list:
    """extract select attributes from a packet"""
    l4_proto = None
    if TCP in pkt:
        l4_proto = TCP
    elif UDP in pkt:
        l4_proto = UDP
    pkt_attrs = [
        float(pkt.time),
        pkt.getlayer(l4_proto).name,
        pkt[IP].src,
        pkt[IP].dst,
        pkt[l4_proto].sport,
        pkt[l4_proto].dport,
        len(pkt),
    ]

    pkt_time_str = str(datetime.fromtimestamp(float(pkt.time), timezone.utc))
    dbg_print(
        "[{}] {} {}:{} -> {}:{} - {} bytes".format(
            pkt_time_str,
            pkt.getlayer(l4_proto).name,
            pkt[IP].src,
            pkt[l4_proto].sport,
            pkt[IP].dst,
            pkt[l4_proto].dport,
            len(pkt),
        )
    )

    return pkt_attrs


def create_pkt_object(pkt: Packet) -> dict:
    """create a dictionary of packet attributes"""
    """key: attribute name, value: attribute value"""

    l4_proto = None
    if TCP in pkt:
        l4_proto = TCP
    elif UDP in pkt:
        l4_proto = UDP

    pkt_time_str = str(datetime.fromtimestamp(float(pkt.time), timezone.utc))

    res_json = {
        "time": float(pkt.time),
        "l4_proto": pkt.getlayer(l4_proto).name,
        "src_addr": pkt[IP].src,
        "dst_addr": pkt[IP].dst,
        "src_port": pkt[l4_proto].sport,
        "dst_port": pkt[l4_proto].dport,
        "pkt_len": len(pkt),
    }

    return res_json


def row_to_dict(pkt_row: list) -> dict:
    """make dict from CSV row"""

    return {
        "time": float(pkt_row[0]),
        "l4_proto": pkt_row[1],
        "src_addr": pkt_row[2],
        "dst_addr": pkt_row[3],
        "src_port": int(pkt_row[4]),
        "dst_port": int(pkt_row[5]),
        "pkt_len": int(pkt_row[6]),
    }


def prep_csv(out_file: str):
    with open(out_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # header row
        writer.writerow(
            [
                "time",
                "l4_proto",
                "src_addr",
                "dst_addr",
                "src_port",
                "dst_port",
                "pkt_len",
            ]
        )


def pkts_write_csv(pkts: list, out_file: str):
    with open(out_file, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(pkts)


if __name__ == "__main__":
    argp = ArgumentParser()
    argp.add_argument("-f", "--pcap_file", required=False, dest="_pcap")
    argp.add_argument("-c", "--csv_file", required=False, dest="_csv")
    argp.add_argument("-o", "--out_file", required=False, dest="_out")
    argp.add_argument(
        "--stream_size", required=False, default=10000, dest="_streamsize"
    )
    argp.add_argument(
        "-x",
        "--sample",
        required=False,
        default=False,
        dest="_sample",
        action="store_true",
    )
    argp.add_argument(
        "-s",
        "--stream",
        required=False,
        default=False,
        dest="_stream",
        action="store_true",
    )
    argp.add_argument(
        "-d",
        "--debug",
        required=False,
        default=False,
        dest="_debug",
        action="store_true",
    )
    args = argp.parse_args()

    pcap_file = args._pcap
    csv_file = args._csv
    out_file = args._out
    streaming = args._stream
    sample = args._sample

    DEBUG = args._debug

    sample_size = int(args._streamsize)  # 100000
    batch_size = 100  # 100000

    # if preprocessed data ready for streaming
    if csv_file:
        with open(csv_file, newline="") as f:
            csv_rdr = csv.reader(f)
            next(csv_rdr)  # skip headers
            pkts = []

            print("started stream from csv")
            for idx, row in enumerate(csv_rdr):
                # direct streaming to kafka goes here
                producer.client.send(KAFKA_TOPIC, row_to_dict(row))
                dbg_print(row_to_dict(row))
                dbg_print("streamed packet", idx)
                if sample and idx > sample_size:
                    break
            print(f"total streamed: {idx}")

    # otherwise, process packets
    else:
        pcap_rdr = PcapReader(pcap_file)
        if not streaming:
            assert args._out and args._out != ""
            prep_csv(out_file)

        pkts = []
        cnt = 0
        seen_count = 0

        print("started stream from pcap")
        for idx, pkt in enumerate(pcap_rdr):
            seen_count += 1
            # filter packets
            if not pkt_filter(pkt):
                continue

            if not streaming:
                # write to file
                pkts.append(pkt_extract(pkt))

                if sample and idx > sample_size:
                    break

                if idx > 0 and idx % batch_size == 0:
                    pkts_write_csv(pkts, out_file)
                    pkts = []
            else:
                # direct streaming to kafka goes here
                packet_data = create_pkt_object(pkt)
                producer.client.send(KAFKA_TOPIC, packet_data)
                cnt += 1
                # print(f"streamed packet at index {idx} ")
                if idx > sample_size:
                    break

        print(f"total seen: {seen_count-1}")
        print(f"total streamed: {cnt}")
        # flush remaining
        if not streaming and len(pkts) > 0:
            pkts_write_csv(pkts, out_file)
