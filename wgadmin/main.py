# PYTHON_ARGCOMPLETE_OK
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

import argcomplete

from wgadmin.subcommands import (
    add_connection,
    add_peer,
    generate_all_configs,
    generate_config,
    list_peers,
    new_network,
)

parser = argparse.ArgumentParser(
    description="Create and manage WireGuard VPNs", allow_abbrev=False,
)
subparsers = parser.add_subparsers(description="subcommand to run", required=True)

new_network.create_parser(subparsers)
list_peers.create_parser(subparsers)
add_peer.create_parser(subparsers)
add_connection.create_parser(subparsers)
generate_config.create_parser(subparsers)
generate_all_configs.create_parser(subparsers)


argcomplete.autocomplete(parser)


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
