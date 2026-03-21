#!/usr/bin/env python3
"""Generate normal or attack TCP traffic on dummy0 for NWDAF testing."""

import argparse
import random
import time

from scapy.all import IP, TCP, Raw, send


def _send_packets(pkts: list, iface: str, delay: float):
    for i, pkt in enumerate(pkts):
        send(pkt, iface=iface, verbose=False)
        if delay:
            time.sleep(delay)
        if (i + 1) % 500 == 0:
            print(f"  sent {i + 1}/{len(pkts)}")
    print(f"[+] Done: {len(pkts)} packets")


# ── Normal traffic ──────────────────────────────────────────────────

def normal(target: str, iface: str, count: int, delay: float):
    """Simulate realistic HTTP/HTTPS browsing traffic.

    Characteristics vs attack:
    - Mixed flags: SYN → SYN-ACK → ACK → PSH-ACK → FIN (full handshake)
    - Varied packet sizes (headers, small requests, large responses)
    - Normal TTL values (54-64)
    - Varied window sizes (8192-65535)
    """
    print(f"[~] Normal traffic → {target} ({count} packets)")
    pkts = []
    ports = [80, 443, 8080, 8443]

    for _ in range(count):
        dport = random.choice(ports)
        sport = random.randint(1024, 65535)

        # Simulate a TCP conversation flow
        phase = random.choices(
            ["syn", "synack", "ack", "data", "fin"],
            weights=[10, 10, 20, 50, 10],
        )[0]

        if phase == "syn":
            flags, window, payload = "S", random.randint(8192, 65535), b""
        elif phase == "synack":
            flags, window, payload = "SA", random.randint(8192, 65535), b""
        elif phase == "ack":
            flags, window, payload = "A", random.randint(16384, 65535), b""
        elif phase == "data":
            flags, window = "PA", random.randint(16384, 65535)
            payload = random.randbytes(random.randint(64, 1400))
        else:  # fin
            flags, window, payload = "FA", random.randint(8192, 65535), b""

        pkt = (
            IP(dst=target, ttl=random.randint(54, 64))
            / TCP(sport=sport, dport=dport, flags=flags, window=window)
        )
        if payload:
            pkt = pkt / Raw(load=payload)
        pkts.append(pkt)

    _send_packets(pkts, iface, delay)


# ── Attack traffic ──────────────────────────────────────────────────

def syn_flood(target: str, iface: str, count: int, delay: float):
    """SYN flood: 100% SYN, no ACK, uniform small packets, fixed window."""
    print(f"[!] SYN Flood → {target}:80 ({count} packets)")
    pkts = [
        IP(dst=target, ttl=64)
        / TCP(sport=random.randint(1024, 65535), dport=80, flags="S", window=1024)
        for _ in range(count)
    ]
    _send_packets(pkts, iface, delay)


def rst_flood(target: str, iface: str, count: int, delay: float):
    """RST flood: 100% RESET, window=0."""
    print(f"[!] RST Flood → {target}:80 ({count} packets)")
    pkts = [
        IP(dst=target, ttl=64)
        / TCP(sport=random.randint(1024, 65535), dport=80, flags="R", window=0)
        for _ in range(count)
    ]
    _send_packets(pkts, iface, delay)


def mixed_attack(target: str, iface: str, count: int, delay: float):
    """Mix of SYN, RST with abnormal TTL and window sizes."""
    print(f"[!] Mixed attack → {target} ({count} packets)")
    pkts = []
    for _ in range(count):
        pkt = (
            IP(dst=target, ttl=random.choice([1, 64, 255]))
            / TCP(
                sport=random.randint(1024, 65535),
                dport=random.choice([80, 443, 8080]),
                flags=random.choice(["S", "S", "S", "R", "SA"]),
                window=random.choice([0, 1024, 1024, 1024]),
            )
        )
        pkts.append(pkt)
    _send_packets(pkts, iface, delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP traffic generator for NWDAF testing")
    parser.add_argument(
        "mode",
        choices=["normal", "syn", "rst", "mixed"],
        help="normal = browsing traffic, syn/rst/mixed = attacks",
    )
    parser.add_argument("-c", "--count", type=int, default=10000)
    parser.add_argument("-d", "--delay", type=float, default=0.001, help="Delay between packets (s)")
    parser.add_argument("-I", "--iface", default="dummy0")
    parser.add_argument("-t", "--target", default="10.0.0.1")
    args = parser.parse_args()

    modes = {"normal": normal, "syn": syn_flood, "rst": rst_flood, "mixed": mixed_attack}
    modes[args.mode](args.target, args.iface, args.count, args.delay)
