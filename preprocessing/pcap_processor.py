from argparse import ArgumentParser
from datetime import datetime, timezone
import csv

from scapy.packet import Packet
from scapy.utils import PcapReader
from scapy.layers.inet import IP, TCP, UDP

from kafka import KafkaProducer
import json

dbg_print = lambda *x: DEBUG and print(f"[DEBUG] {x}")

# Kafka Configuration
KAFKA_TOPIC = 'pcap_stream'
KAFKA_SERVER = 'localhost:9092'  # Adjust to your Kafka server

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    #value_serializer=lambda v: json.dumps(v).encode('utf-8')  # Encode data as JSON
    value_serializer=lambda v: v.encode('utf-8') if isinstance(v, str) else str(v).encode('utf-8') #remove intermediate JSON encoding
)


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
        "pkt_len": len(pkt)
    }

    return res_json

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
    argp.add_argument("-f", "--pcap_file", required=True, dest="_pcap")
    argp.add_argument("-o", "--out_file", required=False, dest="_out")
    argp.add_argument("--stream_size", required=False, default=10000, dest="_streamsize")
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
    out_file = args._out
    streaming = args._stream
    sample = args._sample
    samplesize = int(args._streamsize)

    DEBUG = args._debug

    sample_size = samplesize #1000000
    batch_size = 100 #100000

    pcap_rdr = PcapReader(pcap_file)
    if not streaming:
        assert args._out and args._out != ""
        prep_csv(out_file)

    pkts = []
    for idx, pkt in enumerate(pcap_rdr):
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
            producer.send(KAFKA_TOPIC, packet_data)
            print(f"streamed packet at index {idx} ")
            if idx > sample_size: break
    
    # flush remaining
    if not streaming and len(pkts) > 0:
        pkts_write_csv(pkts, out_file)

