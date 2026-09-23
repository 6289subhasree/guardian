from datetime import datetime, timezone

from scapy.layers.inet import IP, TCP, UDP


# Maps a TCP flow to the GUARDIAN-X device that identified itself in that flow.
tcp_flow_devices = {}


def get_tcp_flow_key(ip_layer, tcp_layer):
    """
    Return a direction-independent key for a TCP flow.

    The same key is produced for both directions of the connection.
    """

    endpoint_a = (ip_layer.src, tcp_layer.sport)
    endpoint_b = (ip_layer.dst, tcp_layer.dport)

    return tuple(sorted((endpoint_a, endpoint_b)))


def extract_device_id_from_payload(payload: bytes):
    """
    Extract a GUARDIAN-X device ID from an HTTP heartbeat request.

    Example:
        POST /devices/ESP32-001/heartbeat HTTP/1.1

    Returns:
        The device ID if found, otherwise None.
    """

    try:
        text = payload.decode("utf-8", errors="ignore")

        marker = "/devices/"
        suffix = "/heartbeat"

        start = text.find(marker)

        if start == -1:
            return None

        start += len(marker)

        end = text.find(suffix, start)

        if end == -1:
            return None

        device_id = text[start:end]

        if device_id:
            return device_id

    except Exception:
        return None

    return None


def parse_packet(packet):
    """
    Convert a Scapy packet into a structured network observation.
    """

    if not packet.haslayer(IP):
        return None

    ip_layer = packet[IP]

    observation = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": ip_layer.src,
        "destination_ip": ip_layer.dst,
        "protocol": ip_layer.proto,
        "packet_length": len(packet),
        "source_port": None,
        "destination_port": None,
        "tcp_flags": None,
        "payload_length": 0,
        "device_id": None,
    }

    if packet.haslayer(TCP):
        tcp_layer = packet[TCP]

        observation["source_port"] = tcp_layer.sport
        observation["destination_port"] = tcp_layer.dport
        observation["protocol"] = "TCP"
        observation["tcp_flags"] = str(tcp_layer.flags)

        # Identify the TCP flow independently of packet direction.
        flow_key = get_tcp_flow_key(ip_layer, tcp_layer)

        if tcp_layer.payload:
            payload = bytes(tcp_layer.payload)

            observation["payload_length"] = len(payload)

            # First try to identify the device directly from this packet.
            device_id = extract_device_id_from_payload(payload)

            if device_id:
                # Remember the device for the entire TCP flow.
                tcp_flow_devices[flow_key] = device_id
                observation["device_id"] = device_id

        # If this packet did not identify a device itself, inherit the
        # device association already learned from another packet in this flow.
        if observation["device_id"] is None:
            observation["device_id"] = tcp_flow_devices.get(flow_key)

    elif packet.haslayer(UDP):
        udp_layer = packet[UDP]

        observation["source_port"] = udp_layer.sport
        observation["destination_port"] = udp_layer.dport
        observation["protocol"] = "UDP"

        if udp_layer.payload:
            observation["payload_length"] = len(udp_layer.payload)

    else:
        observation["protocol"] = ip_layer.proto

    return observation
