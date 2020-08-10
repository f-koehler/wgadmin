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

import jinja2

from wgadmin.network import Network


def generate_config(args: argparse.Namespace):
    net = Network.from_file(args.config)
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("wgadmin", "templates"), autoescape=True
    )
    template = env.get_template(args.config_format)

    config = template.render(peer=net.peers[args.name])
    if not args.output:
        print(config)
        return

    with open(args.output, "w") as fptr:
        fptr.write(config)


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "generate-config", help="generate a config file for a peer"
    )
    parser.set_defaults(func=generate_config)

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.yml"),
        help="path of the config file",
    )
    parser.add_argument("-o", "--output", type=Path, help="name of the output file")
    parser.add_argument("name", type=str, help="name of the peer")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--nm",
        "--network-manager",
        action="store_const",
        const="nm-connection",
        dest="config_format",
        help="create a configuration file for NetworkManager",
    )
    group.add_argument(
        "--wq",
        "--wg-quick",
        action="store_const",
        const="wg-quick",
        dest="config_format",
        help="create a configuration file to be used with wg-quick",
    )

    return parser
