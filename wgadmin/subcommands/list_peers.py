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


def list_peers(args: argparse.Namespace):
    net = Network.from_file(args.config)
    if not args.verbose:
        for peer_name in net.peers:
            print(peer_name)
        return

    # TODO: implement verbose version


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser("list-peers", help="list the peers in a network")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.yml"),
        help="path of the config file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="whether to print detailed information about each peer",
    )
    parser.set_defaults(func=list_peers)

    return parser
