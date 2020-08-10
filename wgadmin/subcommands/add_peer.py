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

import argparse
from pathlib import Path
from typing import Union

from wgadmin.peer import Peer
from wgadmin.network import Network


def sanitize_port(value: Union[str, int]) -> int:
    port = int(value)
    if (port < 0) or (port > 65535):
        raise argparse.ArgumentTypeError("invalid port number: {}".format(port))
    return port


def add_peer(args: argparse.Namespace):
    net = Network.from_file(args.config)

    if (args.name in net.peers) and not args.force:
        raise RuntimeError(
            'peer "{}" already present, add -f flag to overwrite'.format(args.name)
        )

    ipv4 = args.ipv4
    if (not ipv4) and net.ipv4:
        ipv4 = str(net.get_next_ipv4_address())
    ipv6 = args.ipv6
    if (not ipv6) and net.ipv6:
        ipv6 = str(net.get_next_ipv6_address())
    net.peers[args.name] = Peer(
        name=args.name,
        interface=args.interface,
        ipv4=ipv4,
        ipv6=ipv6,
        port=args.port,
        endpoint_address=args.endpoint_address,
    )

    net.to_file(args.config)


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("add-peer", help="add a peer to a network")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.yml"),
        help="path of the config file",
    )
    parser.add_argument("name", type=str, help="name for the peer")
    parser.add_argument(
        "--ipv4", type=str, default="", help="IPv4 address of the peer inside the VPN"
    )
    parser.add_argument(
        "--ipv6", type=str, default="", help="IPv6 address of the peer inside the VPN"
    )
    parser.add_argument(
        "--port",
        type=sanitize_port,
        default=51902,
        help="port for WireGuard to listen on",
    )
    parser.add_argument(
        "-e",
        "--endpoint-address",
        type=str,
        default="",
        help="make the peer an endpoint addressable under this address",
    )
    parser.add_argument(
        "-i",
        "--interface",
        type=str,
        default="wg0",
        help="name of the WireGuard network interface that will created",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether to overwrite an existing peer",
    )
    parser.set_defaults(func=add_peer)

    return parser
