# PYTHON_ARGCOMPLETE_OK
import argparse
import argcomplete

from wgadmin.subcommands import (
    new_network,
    list_peers,
    add_peer,
    add_connection,
    generate_all_configs,
)


parser = argparse.ArgumentParser(
    description="Create, manage and deploy a WireGuard VPN", allow_abbrev=False,
)
subparsers = parser.add_subparsers(description="subcommand to run", required=True)

new_network.create_parser(subparsers)
list_peers.create_parser(subparsers)
add_peer.create_parser(subparsers)
add_connection.create_parser(subparsers)
generate_all_configs.create_parser(subparsers)


argcomplete.autocomplete(parser)


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
