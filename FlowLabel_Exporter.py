from scapy.all import sniff, IPv6
from prometheus_client import start_http_server, Gauge
import time
import threading
from collections import defaultdict

packet_timestamps = defaultdict(list)
packet_counts = {}

ipv6_gauges_transmitting = {}
ipv6_gauges_receiving = {}

monitoring_ips = {
    "s1-eth1": "bbff::11",
    "s1-eth2": "bbff::22",
    "s1-eth3": "aadd::11",
}

TIME_WINDOW = 15.0

def get_gauge(interface, direction):
    if direction == "transmitting":
        if interface not in ipv6_gauges_transmitting:
            ipv6_gauges_transmitting[interface] = Gauge(
                f"transmitting_{interface.replace('-', '_')}",
                f"Transmitted on {interface}",
                ["src", "dst", "scitags"]
            )
        return ipv6_gauges_transmitting[interface]
    
    elif direction == "receiving":
        if interface not in ipv6_gauges_receiving:
            ipv6_gauges_receiving[interface] = Gauge(
                f"receiving_{interface.replace('-', '_')}",
                f"Received on {interface}",
                ["src", "dst", "scitags"]
            )
        return ipv6_gauges_receiving[interface]

def packet_callback(packet):
    if IPv6 in packet:
        src_ip = packet[IPv6].src
        dst_ip = packet[IPv6].dst
        flow_label = packet[IPv6].fl
        iface = packet.sniffed_on

        if iface not in monitoring_ips:
            return

        monitoring_ip = monitoring_ips[iface]

        label = str(bin(flow_label))[2:].zfill(20)
        activity = int(label[12:18], 2)
        experiment = int(label[2:11][::-1], 2)
        scitags = f"{activity} {experiment}"

        if src_ip == monitoring_ip:
            direction = "transmitting"
        elif dst_ip == monitoring_ip:
            direction = "receiving"
        else:
            return 

        print(f"IPv6 {direction.upper()} Packet on {iface}: {src_ip} -> {dst_ip}, Flow Label: {flow_label}, Scitags: {scitags}")

        gauge = get_gauge(iface, direction)

        scitags_label = scitags if scitags == "14 16" else "others"
        
        count_key = (iface, direction, src_ip, dst_ip, scitags_label)
        packet_timestamps[count_key].append(time.time())

def update_metrics():
    while True:
        current_time = time.time()

        for count_key in list(packet_timestamps.keys()):
            iface, direction, src_ip, dst_ip, scitags_label = count_key

            packet_timestamps[count_key] = [
                ts for ts in packet_timestamps[count_key] if current_time - ts <= TIME_WINDOW
            ]

            packet_count = len(packet_timestamps[count_key])

            packet_counts[count_key] = packet_count

            gauge = get_gauge(iface, direction)
            gauge.labels(src=src_ip, dst=dst_ip, scitags=scitags_label).set(packet_count)

        time.sleep(TIME_WINDOW)

threading.Thread(target=update_metrics, daemon=True).start()
start_http_server(9101)

print("Listening...")
sniff(iface=["s1-eth1", "s1-eth2", "s1-eth3"], prn=packet_callback, store=0)
