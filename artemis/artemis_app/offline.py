"""Opt-in offline admission for configured engines; no DNS guessing/auto-downloads.

A fixed literal private WSL/LAN address can be explicitly authorized without
classifying it as Internet inference. This is application policy, not a host
firewall or a guarantee about optional engines' own behavior.
"""
import ipaddress
import os
from urllib.parse import urlparse

LOCAL_NETWORKS = tuple(ipaddress.ip_network(s) for s in
                       ('127.0.0.0/8', '10.0.0.0/8', '172.16.0.0/12',
                        '192.168.0.0/16', '::1/128', 'fc00::/7'))


def enabled():
    return os.environ.get('ARTEMIS_OFFLINE', '').lower() in ('1', 'true', 'yes')


def local_endpoint(url):
    host = urlparse(url).hostname
    if host == 'localhost':
        return True
    try:
        address = ipaddress.ip_address(host)
        return any(address in network for network in LOCAL_NETWORKS)
    except (ValueError, TypeError):
        return False


def admit_endpoint(url):
    if enabled() and not local_endpoint(url):
        raise ValueError('Offline mode permits only loopback or an explicitly configured literal private WSL/LAN endpoint; Internet/DNS endpoints are disabled')
