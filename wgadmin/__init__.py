#!/usr/bin/env python
from __future__ import annotations
import subprocess
import json
from typing import Tuple, Union, Any, List, Optional, Dict, Set
from pathlib import Path
from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network

__version__ = "0.1.0"


def generate_public_key(private_key: str) -> str:
    return (
        subprocess.check_output(["/usr/bin/wg", "pubkey"], input=private_key.encode())
        .decode()
        .strip()
    )


def generate_private_key() -> str:
    return subprocess.check_output(["/usr/bin/wg", "genkey"]).decode().strip()


def generate_keypair() -> Tuple[str, str]:
    private = generate_private_key()
    return private, generate_public_key(private)


def generate_psk() -> str:
    return subprocess.check_output(["/usr/bin/wg", "genpsk"]).decode().strip()


def load_config(path: Union[str, Path] = "config.json") -> Any:
    with open(path, "r") as fptr:
        return json.load(fptr)


class Peer:
    def __init__(
        self,
        name: str,
        interface: str = "wg0",
        ipv4: str = "",
        ipv6: str = "",
        port: int = 51902,
        private_key: Optional[str] = None,
        public_key: Optional[str] = None,
        endpoint_address: str = "",
    ):
        self.name = name
        self.interface = interface
        self.address_ipv4 = ipv4
        self.address_ipv6 = ipv6
        self.port = port

        if private_key:
            self.private_key = private_key
        else:
            self.private_key = generate_private_key()

        if public_key:
            self.public_key = public_key
        else:
            self.public_key = generate_public_key(self.private_key)

        self.endpoint_address = endpoint_address

        self.connections: List[Connection] = []

    def add_connection(self, peer_b: Peer, psk: str = ""):
        connection = Connection(self, peer_b, psk)
        self.connections.append(connection)

        peer_b.connections.append(Connection(peer_b, self, connection.psk))


class Connection:
    def __init__(self, peer_a: Peer, peer_b: Peer, psk: str = ""):
        self.peer_a = peer_a
        self.peer_b = peer_b

        if psk:
            self.psk = psk
        else:
            self.psk = generate_psk()


class Network:
    def __init__(
        self,
        ipv4: bool = True,
        ipv6: bool = True,
        ipv4_range: str = "10.0.0.0/24",
        ipv6_range: str = "fdc9:281f:4d7:9ee9::/64",
    ):
        self.peers: Dict[str, Peer] = {}
        self.ipv4: bool = ipv4
        self.ipv6: bool = ipv6
        self.ipv4_range: str = ipv4_range
        self.ipv6_range: str = ipv6_range

    def get_used_ipv4_addresses(self) -> Set[IPv4Address]:
        addresses: Set[IPv4Address] = set()
        for name in self.peers:
            if self.peers[name].address_ipv4:
                addresses.add(IPv4Address(self.peers[name].address_ipv4))
        return addresses

    def get_used_ipv6_addresses(self) -> Set[IPv6Address]:
        addresses: Set[IPv6Address] = set()
        for name in self.peers:
            if self.peers[name].address_ipv6:
                addresses.add(IPv6Address(self.peers[name].address_ipv6))
        return addresses

    def get_next_ipv4_address(self) -> IPv4Address:
        addresses = self.get_used_ipv4_addresses()
        for address in IPv4Network(self.ipv4_range).hosts():
            if address in addresses:
                continue
            return address

        raise RuntimeError("No more IPv4 addresses available")

    def get_next_ipv6_address(self) -> IPv6Address:
        addresses = self.get_used_ipv6_addresses()
        for address in IPv6Network(self.ipv6_range).hosts():
            if address in addresses:
                continue
            return address

        raise RuntimeError("No more IPv6 addresses available")

    def to_json(self) -> str:
        peer_dict: Dict[str, Dict[str, str]] = {}
        connection_list: List[Dict[str, str]] = []
        settings = {
            "ipv4": self.ipv4,
            "ipv6": self.ipv6,
            "ipv4_range": self.ipv4_range,
            "ipv6_range": self.ipv6_range,
        }

        for peer_name in self.peers:
            peer = self.peers[peer_name]
            peer_dict[peer.name] = {
                "name": peer.name,
                "interface": peer.interface,
                "ipv4": peer.address_ipv4,
                "ipv6": peer.address_ipv6,
                "port": str(peer.port),
                "private_key": peer.private_key,
                "public_key": peer.public_key,
                "endpoint_address": peer.endpoint_address,
            }
            for connection in peer.connections:
                if connection.peer_a.name > connection.peer_b.name:
                    continue
                connection_list.append(
                    {
                        "peer_a": connection.peer_a.name,
                        "peer_b": connection.peer_b.name,
                        "psk": connection.psk,
                    }
                )

        return json.dumps(
            {"settings": settings, "peers": peer_dict, "connections": connection_list}
        )

    def to_json_file(self, path: Union[str, Path]):
        with open(path, "w") as fptr:
            fptr.write(self.to_json())

        if Path("/usr/bin/prettier").exists():
            subprocess.run(
                ["/usr/bin/prettier", "--parser", "json", "--write", str(path)]
            )

    @staticmethod
    def from_json(config: str) -> Network:
        decoded = json.loads(config)

        settings = decoded["settings"]
        net = Network(
            ipv4=settings["ipv4"],
            ipv6=settings["ipv6"],
            ipv4_range=settings["ipv4_range"],
            ipv6_range=settings["ipv6_range"],
        )

        for peer_name in decoded["peers"]:
            peer_entry = decoded["peers"][peer_name]
            net.peers[peer_name] = Peer(
                name=peer_name,
                interface=peer_entry["interface"],
                ipv4=peer_entry["ipv4"],
                ipv6=peer_entry["ipv6"],
                port=int(peer_entry["port"]),
                private_key=peer_entry["private_key"],
                public_key=peer_entry["public_key"],
                endpoint_address=peer_entry["endpoint_address"],
            )

        for connection_entry in decoded["connections"]:
            net.peers[connection_entry["peer_a"]].add_connection(
                connection_entry["peer_b"], connection_entry["psk"]
            )

        return net

    @staticmethod
    def from_json_file(path: Union[Path, str]) -> Network:
        with open(path, "r") as fptr:
            return Network.from_json(fptr.read())
