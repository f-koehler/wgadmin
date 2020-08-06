#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import argparse
from pathlib import Path
import jinja2
import argcomplete

from wgadmin.peer import Peer
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
    net.to_json_file(args.config)


def add_connection(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    net.peers[args.peer_a].add_connection(net.peers[args.peer_b])
    net.to_json_file(args.config)


def generate_config(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("wgadmin", "templates"), autoescape=True
    )
    template = env.get_template("nm-connection")
    for name in net.peers:
        with open(name + ".nmconnection", "w") as fptr:
            fptr.write(template.render(peer=net.peers[name]))
    template = env.get_template("wg-quick")
    for name in net.peers:
        with open(name + ".conf", "w") as fptr:
            fptr.write(template.render(peer=net.peers[name]))


def sanitize_port(value) -> int:
    port = int(value)
    if (port < 0) or (port > 65535):
        raise argparse.ArgumentTypeError("invalid port number: {}".format(port))
    return port


parser = argparse.ArgumentParser(
    description="Create, manage and deploy a WireGuard VPN", allow_abbrev=False,
)
subparsers = parser.add_subparsers(description="subcommand to run", required=True)

parser_new_network = subparsers.add_parser(
    "new-network", help="create a new, empty network"
)
parser_new_network.set_defaults(func=new_network)
parser_new_network.add_argument(
    "-c",
    "--config",
    type=Path,
    default=Path("wg.json"),
    help="path of the config file",
)
parser_new_network.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="whether to overwrite and existing config file",
)
parser_new_network.add_argument(
    "--ipv4",
    action="store_true",
    dest="ipv4",
    default=True,
    help="automatically assign IPv4 addresses",
)
parser_new_network.add_argument(
    "--no-ipv4",
    action="store_false",
    dest="ipv4",
    help="do not automatically assign IPv4 addresses",
)
parser_new_network.add_argument(
    "--ipv4-range", type=str, default="10.0.0.0/24", help="IPv4 address range to use",
)
parser_new_network.add_argument(
    "--ipv6",
    action="store_true",
    dest="ipv6",
    default=True,
    help="automatically assign IPv6 addresses",
)
parser_new_network.add_argument(
    "--no-ipv6",
    action="store_false",
    dest="ipv6",
    help="do not automatically assign IPv6 addresses",
)
parser_new_network.add_argument(
    "--ipv6-range",
    type=str,
    default="fdc9:281f:4d7:9ee9::/64",
    help="IPv6 address range to use",
)

parser_list_peers = subparsers.add_parser(
    "list-peers", help="list the peers in a network"
)
parser_list_peers.add_argument(
    "-c",
    "--config",
    type=Path,
    default=Path("wg.json"),
    help="path of the config file",
)
parser_list_peers.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="whether to print detailed information about each peer",
)
parser_list_peers.set_defaults(func=list_peers)

parser_add_peer = subparsers.add_parser("add-peer", help="add a peer to a network")
parser_add_peer.add_argument(
    "-c",
    "--config",
    type=Path,
    default=Path("wg.json"),
    help="path of the config file",
)
parser_add_peer.add_argument("name", type=str, help="name for the peer")
parser_add_peer.add_argument(
    "--ipv4", type=str, default="", help="IPv4 address of the peer inside the VPN"
)
parser_add_peer.add_argument(
    "--ipv6", type=str, default="", help="IPv6 address of the peer inside the VPN"
)
parser_add_peer.add_argument(
    "--port", type=sanitize_port, default=51902, help="port for WireGuard to listen on",
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
    "-f", "--force", action="store_true", help="whether to overwrite an existing peer",
)
parser_add_peer.set_defaults(func=add_peer)

parser_add_connection = subparsers.add_parser(
    "add-connection", help="add a new connections between two peers"
)
parser_add_connection.add_argument(
    "-c",
    "--config",
    type=Path,
    default=Path("wg.json"),
    help="path of the config file",
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

parser_generate_config = subparsers.add_parser(
    "generate-config", help="generate peer configuration files"
)
parser_generate_config.add_argument(
    "-c",
    "--config",
    type=Path,
    default=Path("wg.json"),
    help="path of the config file",
)
parser_generate_config.set_defaults(func=generate_config)

argcomplete.autocomplete(parser)


def main():
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
