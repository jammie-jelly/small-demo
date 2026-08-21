import os
from ipaddress import ip_network

DEFAULT_ALLOWED_NETWORKS = "127.0.0.0/8,::1/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
DEFAULT_TRUSTED_PROXIES = "127.0.0.1/32,::1/128"


def _parse_networks(spec: str, default: str):
    nets = []
    for raw in spec.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            nets.append(ip_network(raw, strict=False))
        except ValueError:
            continue
    if not nets and default:
        nets = [ip_network(n) for n in default.split(",")]
    return nets


def _parse_trusted(spec: str) -> list[str]:
    """Trusted proxy hosts as raw strings (uvicorn parses CIDRs and '*')."""
    hosts = [raw.strip() for raw in spec.split(",") if raw.strip()]
    return hosts or DEFAULT_TRUSTED_PROXIES.split(",")


allowed_networks = _parse_networks(os.environ.get("DEMO_ALLOWED_NETWORKS", ""), DEFAULT_ALLOWED_NETWORKS)
trusted_proxies = _parse_trusted(os.environ.get("DEMO_TRUSTED_PROXY", ""))
