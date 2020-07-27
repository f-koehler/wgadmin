import argparse
from pathlib import Path

from wgadmin import Network, Peer


def new_network(args: argparse.Namespace):
    if args.config.exists():
        if not args.force:
            raise RuntimeError(
                'config "{}" already exists, add -f flag to overwrite'.format(
                    args.config
                )
            )

    net = Network()
    net.to_json_file(args.config)


def list_peers(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    if not args.verbose:
        for peer_name in net.peers:
            print(peer_name)
        return

    # TODO: implement verbose version


def add_peer(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    if (args.name in net.peers) and not args.force:
        raise RuntimeError(
            'peer "{}" already present, add -f flag to overwrite'.format(args.name)
        )
    net.peers[args.name] = Peer(
        name=args.name,
        interface=args.interface,
        ipv4=args.ipv4,
        ipv6=args.ipv6,
        port=args.port,
        endpoint_address=args.endpoint_address,
    )
    net.to_json_file(args.config)


def add_connection(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    net.peers[args.peer_a].add_connection(net.peers[args.peer_b])
    net.to_json_file(args.config)


def sanitize_port(value) -> int:
    port = int(value)
    if (port < 0) or (port > 65535):
        raise argparse.ArgumentTypeError("invalid port number: {}".format(port))
    return port


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create, manage and deploy a WireGuard VPN", allow_abbrev=False,
    )
    subparsers = parser.add_subparsers(description="subcommand to run", required=True)

    parser_new_network = subparsers.add_parser(
        "new-network", help="create a new, empty network"
    )
    parser_new_network.set_defaults(func=new_network)
    parser_new_network.add_argument("config", type=Path, help="path of the config file")
    parser_new_network.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether to overwrite and existing config file",
    )

    parser_list_peers = subparsers.add_parser(
        "list-peers", help="list the peers in a network"
    )
    parser_list_peers.add_argument("config", type=Path, help="path of the config file")
    parser_list_peers.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="whether to print detailed information about each peer",
    )
    parser_list_peers.set_defaults(func=list_peers)

    parser_add_peer = subparsers.add_parser("add-peer", help="add a peer to a network")
    parser_add_peer.add_argument("config", type=Path, help="path of the config file")
    parser_add_peer.add_argument("name", type=str, help="name for the peer")
    parser_add_peer.add_argument(
        "--ipv4", type=str, default="", help="IPv4 address of the peer inside the VPN"
    )
    parser_add_peer.add_argument(
        "--ipv6", type=str, default="", help="IPv6 address of the peer inside the VPN"
    )
    parser_add_peer.add_argument(
        "--port",
        type=sanitize_port,
        default=51902,
        help="port for WireGuard to listen on",
    )
    parser_add_peer.add_argument(
        "-e",
        "--endpoint-address",
        type=str,
        default="",
        help="make the peer an endpoint addressable under this address",
    )
    parser_add_peer.add_argument(
        "-i",
        "--interface",
        type=str,
        default="wg0",
        help="name of the WireGuard network interface that will created",
    )
    parser_add_peer.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether to overwrite an existing peer",
    )
    parser_add_peer.set_defaults(func=add_peer)

    parser_add_connection = subparsers.add_parser(
        "add-connection", help="add a new connections between two peers"
    )
    parser_add_connection.add_argument(
        "config", type=Path, help="path of the config file"
    )
    parser_add_connection.add_argument(
        "peer_a", type=str, help="one side of the connection"
    )
    parser_add_connection.add_argument(
        "peer_b", type=str, help="other side of the connection"
    )
    parser_add_connection.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="whether to overwrite an existing connection",
    )
    parser_add_connection.set_defaults(func=add_connection)

    args = parser.parse_args()

    args.func(args)
