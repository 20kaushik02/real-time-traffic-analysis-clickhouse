from datetime import datetime, timezone

from scapy.utils import PcapReader
from scapy.layers.inet import IP, TCP, UDP

pcap_rdr = PcapReader("202310081400.pcap")
sample_size = 100

for idx, pkt in enumerate(pcap_rdr):
    try:
        assert (IP in pkt)
        assert (pkt[IP].version == 4)
        assert (TCP in pkt) or (UDP in pkt)
    except AssertionError:
        continue
    # pkt.show()
    if TCP in pkt:
        print(
            "[{}] TCP {}:{} -> {}:{} - {} bytes".format(
                datetime.fromtimestamp(float(pkt.time), timezone.utc),
                pkt[IP].src,
                pkt[TCP].sport,
                pkt[IP].dst,
                pkt[TCP].dport,
                len(pkt),
            )
        )
    elif UDP in pkt:
        print(
            "[{}] UDP {}:{} -> {}:{} - {} bytes".format(
                datetime.fromtimestamp(float(pkt.time), timezone.utc),
                pkt[IP].src,
                pkt[UDP].sport,
                pkt[IP].dst,
                pkt[UDP].dport,
                len(pkt),
            )
        )

    if idx > sample_size:
        break
