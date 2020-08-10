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

from wgadmin.network import Network


def new_network(args: argparse.Namespace):
    if args.config.exists():
        if not args.force:
            raise RuntimeError(
                'config "{}" already exists, add -f flag to overwrite'.format(
                    args.config
                )
            )

    net = Network(
        ipv4=args.ipv4,
        ipv6=args.ipv6,
        ipv4_range=args.ipv4_range,
        ipv6_range=args.ipv6_range,
    )
    net.to_json_file(args.config)


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("new-network", help="create a new, empty network")
    parser.set_defaults(func=new_network)
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.json"),
        help="path of the config file",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether to overwrite and existing config file",
    )
    parser.add_argument(
        "--ipv4",
        action="store_true",
        dest="ipv4",
        default=True,
        help="automatically assign IPv4 addresses",
    )
    parser.add_argument(
        "--no-ipv4",
        action="store_false",
        dest="ipv4",
        help="do not automatically assign IPv4 addresses",
    )
    parser.add_argument(
        "--ipv4-range",
        type=str,
        default="10.0.0.0/24",
        help="IPv4 address range to use",
    )
    parser.add_argument(
        "--ipv6",
        action="store_true",
        dest="ipv6",
        default=True,
        help="automatically assign IPv6 addresses",
    )
    parser.add_argument(
        "--no-ipv6",
        action="store_false",
        dest="ipv6",
        help="do not automatically assign IPv6 addresses",
    )
    parser.add_argument(
        "--ipv6-range",
        type=str,
        default="fdc9:281f:4d7:9ee9::/64",
        help="IPv6 address range to use",
    )

    return parser
