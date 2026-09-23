"""Host-level MQTT ingress blocking, explicitly opt-in and reversible.

Only the registered device IP and local TCP/1883 are touched. Existing TCP
sessions may persist until reconnect; this is not router-level quarantine.
"""
import ipaddress
import platform
import re
import subprocess


def rule_name(device_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", device_id):
        raise ValueError("Device ID must use letters, numbers, _ or -")
    return f"GUARDIAN-X-{device_id}"


def firewall_command(device_id: str, ip_address: str, enable: bool) -> list[str]:
    ip = str(ipaddress.IPv4Address(ip_address))
    name = rule_name(device_id)
    system = platform.system()
    if system == "Windows":
        if enable:
            return ["netsh", "advfirewall", "firewall", "add", "rule",
                    f"name={name}", "dir=in", "action=block", "protocol=TCP",
                    "localport=1883", f"remoteip={ip}"]
        return ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={name}"]
    if system == "Linux":
        action = "-I" if enable else "-D"
        return ["iptables", action, "INPUT", "-p", "tcp", "-s", ip,
                "--dport", "1883", "-j", "DROP"]
    raise RuntimeError(f"Firewall enforcement unsupported on {system}")


def set_mqtt_block(device_id: str, ip_address: str, enable: bool) -> str:
    cmd = firewall_command(device_id, ip_address, enable)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout or "Firewall command failed").strip())
    return "MQTT ingress blocked" if enable else "MQTT ingress rule removed"
