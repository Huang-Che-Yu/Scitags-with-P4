from scapy.all import sniff, IPv6
from prometheus_client import start_http_server, Gauge

ipv6_gauges_transmitting = {}
ipv6_gauges_receiving = {}

monitoring_ips = {
    "s1-eth1": "bbff::11",
    "s1-eth2": "bbff::22",
    "s1-eth3": "bbff::33",
}

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
        activity = int(label[11:18], 2)
        experiment = int(label[2:12][::-1], 2)
        scitags = f"{activity} {experiment}"

        if src_ip == monitoring_ip:
            direction = "transmitting"
        elif dst_ip == monitoring_ip:
            direction = "receiving"
        else:
            return 

        print(f"IPv6 {direction.upper()} Packet on {iface}: {src_ip} -> {dst_ip}, Flow Label: {flow_label}, Scitags: {scitags}")

        gauge = get_gauge(iface, direction)

        if scitags == "14 16":
            gauge.labels(src=src_ip, dst=dst_ip, scitags=scitags).set(flow_label)
        else:
            gauge.labels(src=src_ip, dst=dst_ip, scitags="others").set(flow_label)

start_http_server(9101)

print("Listening...")
sniff(iface=["s1-eth1", "s1-eth2", "s1-eth3"], prn=packet_callback, store=0)
