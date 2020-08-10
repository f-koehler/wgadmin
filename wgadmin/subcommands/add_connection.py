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

from pathlib import Path
import argparse

from wgadmin.network import Network


def add_connection(args: argparse.Namespace):
    net = Network.from_file(args.config)
    net.peers[args.peer_a].add_connection(net.peers[args.peer_b])
    net.to_file(args.config)


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "add-connection", help="add a new connections between two peers"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.yml"),
        help="path of the config file",
    )
    parser.add_argument("peer_a", type=str, help="one side of the connection")
    parser.add_argument("peer_b", type=str, help="other side of the connection")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether to overwrite an existing connection",
    )
    parser.set_defaults(func=add_connection)

    return parser
