from pathlib import Path
import argparse

from wgadmin.network import Network


def list_peers(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
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
        default=Path("wg0.json"),
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
