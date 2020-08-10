# Copyright (C) 2020  Fabian Köhler <fabian.koehler@protonmail.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import Dict, Set, List, Union
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from pathlib import Path
import json
import yaml

from wgadmin.peer import Peer


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

    def to_yaml(self) -> str:
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

        return yaml.dump(
            {"settings": settings, "peers": peer_dict, "connections": connection_list}
        )

    def to_json_file(self, path: Union[str, Path]):
        with open(path, "w") as fptr:
            fptr.write(self.to_json())

    def to_yaml_file(self, path: Union[str, Path]):
        with open(path, "w") as fptr:
            fptr.write(self.to_yaml())

    def to_file(self, path: Union[str, Path]):
        if Path(path).suffix == ".json":
            self.to_json_file(path)
        else:
            self.to_yaml_file(path)

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
                net.peers[connection_entry["peer_b"]], connection_entry["psk"]
            )

        return net

    @staticmethod
    def from_yaml(config: str) -> Network:
        decoded = yaml.safe_load(config)

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
                net.peers[connection_entry["peer_b"]], connection_entry["psk"]
            )

        return net

    @staticmethod
    def from_json_file(path: Union[Path, str]) -> Network:
        with open(path, "r") as fptr:
            return Network.from_json(fptr.read())

    @staticmethod
    def from_yaml_file(path: Union[Path, str]) -> Network:
        with open(path, "r") as fptr:
            return Network.from_yaml(fptr.read())

    @staticmethod
    def from_file(path: Union[Path, str]) -> Network:
        if Path(path).suffix == ".json":
            return Network.from_json_file(path)
        return Network.from_yaml_file(path)
