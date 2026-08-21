from ipaddress import ip_address

from fastapi import Request

from .config import allowed_networks


def _in_networks(host: str, networks) -> bool:
    try:
        addr = ip_address(host)
    except ValueError:
        return False
    return any(addr in net for net in networks)


def is_local(request: Request) -> bool:
    peer = request.client.host if request.client else ""
    return _in_networks(peer, allowed_networks)
