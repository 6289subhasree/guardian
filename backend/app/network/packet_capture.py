from scapy.all import sniff


def capture_packets(
    interface: str = "eth0",
    packet_count: int = 10,
    timeout: int = 30,
):
    """
    Capture network packets from a specified interface.

    Args:
        interface: Network interface to monitor.
        packet_count: Maximum number of packets to capture.
        timeout: Maximum capture duration in seconds.

    Returns:
        A Scapy packet list containing the captured packets.
    """

    packets = sniff(
        iface=interface,
        count=packet_count,
        timeout=timeout,
    )

    return packets
