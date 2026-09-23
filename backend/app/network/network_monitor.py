from scapy.all import sniff

from app.network.packet_parser import parse_packet
import json
from urllib.request import Request, urlopen


def process_packet(packet):
    """
    Parse a captured packet and return a structured GUARDIAN-X observation.
    """

    observation = parse_packet(packet)

    if observation is None:
        return

    # This capture script runs in a separate process from FastAPI, so send
    # observations through the API rather than writing to process-local memory.
    request = Request(
        "http://127.0.0.1:8000/network/observations",
        data=json.dumps(observation).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=2):
            pass
    except Exception as exc:
        print(f"Observation not delivered to backend: {exc}")

    if observation["protocol"] == "TCP":
        print(
            f"{observation['source_ip']}:{observation['source_port']} "
            f"-> "
            f"{observation['destination_ip']}:{observation['destination_port']} "
            f"| flags={observation['tcp_flags']} "
            f"| payload={observation['payload_length']} "
            f"| device_id={observation['device_id']}"
        )


def start_monitor(
    interface: str = "eth0",
    timeout: int = 30,
):
    """
    Start the GUARDIAN-X network monitoring pipeline.
    """

    print(f"Starting GUARDIAN-X network monitor on {interface}...")
    print(f"Capturing for {timeout} seconds...\n")

    sniff(
        iface=interface,
        prn=process_packet,
        timeout=timeout,
    )

    print("\nGUARDIAN-X network monitor stopped.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Capture traffic visible on a lab interface")
    parser.add_argument("--interface", required=True, help="Interface name shown by Scapy/Npcap")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()
    start_monitor(interface=args.interface, timeout=args.timeout)
