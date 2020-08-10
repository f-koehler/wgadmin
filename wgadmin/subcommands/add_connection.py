from pathlib import Path
import argparse

from wgadmin.network import Network


def add_connection(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    net.peers[args.peer_a].add_connection(net.peers[args.peer_b])
    net.to_json_file(args.config)


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "add-connection", help="add a new connections between two peers"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.json"),
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
