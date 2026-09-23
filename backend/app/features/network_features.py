def extract_network_features(observations: list[dict]) -> dict:
    """
    Aggregate parsed network observations into numerical features.
    """

    packet_count = len(observations)

    if packet_count == 0:
        return {
            "packet_count": 0,
            "total_bytes": 0,
            "avg_packet_size": 0.0,
            "tcp_packet_count": 0,
            "udp_packet_count": 0,
            "unique_destinations": 0,
            "unique_destination_ports": 0,
            "avg_payload_size": 0.0,
            "syn_count": 0,
            "rst_count": 0,
        }

    total_bytes = sum(
        observation["packet_length"]
        for observation in observations
    )

    avg_packet_size = total_bytes / packet_count

    tcp_packet_count = sum(
        1
        for observation in observations
        if observation["protocol"] == "TCP"
    )

    udp_packet_count = sum(
        1
        for observation in observations
        if observation["protocol"] == "UDP"
    )

    unique_destinations = len(
        {
            observation["destination_ip"]
            for observation in observations
        }
    )

    unique_destination_ports = len(
        {
            observation["destination_port"]
            for observation in observations
            if observation["destination_port"] is not None
        }
    )

    avg_payload_size = (
        sum(observation["payload_length"] for observation in observations)
        / packet_count
    )

    syn_count = sum(
        1
        for observation in observations
        if observation["tcp_flags"] is not None
        and "S" in observation["tcp_flags"]
        and "A" not in observation["tcp_flags"]
    )

    rst_count = sum(
        1
        for observation in observations
        if observation["tcp_flags"] is not None
        and "R" in observation["tcp_flags"]
    )

    return {
        "packet_count": packet_count,
        "total_bytes": total_bytes,
        "avg_packet_size": avg_packet_size,
        "tcp_packet_count": tcp_packet_count,
        "udp_packet_count": udp_packet_count,
        "unique_destinations": unique_destinations,
        "unique_destination_ports": unique_destination_ports,
        "avg_payload_size": avg_payload_size,
        "syn_count": syn_count,
        "rst_count": rst_count,
    }
