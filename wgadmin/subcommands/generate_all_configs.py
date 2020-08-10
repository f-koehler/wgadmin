import jinja2
import argparse
from pathlib import Path

from wgadmin.network import Network


def generate_all_configs(args: argparse.Namespace):
    net = Network.from_json_file(args.config)
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("wgadmin", "templates"), autoescape=True
    )

    config_name = Path(args.config).stem
    for name in net.peers:
        directory = Path(config_name) / name

        template = env.get_template("nm-connection")
        directory.mkdir(exist_ok=True, parents=True)
        with open((directory / config_name).with_suffix(".nmconnection"), "w") as fptr:
            fptr.write(template.render(peer=net.peers[name]))

        template = env.get_template("wg-quick")
        with open((directory / config_name).with_suffix(".conf"), "w") as fptr:
            fptr.write(template.render(peer=net.peers[name]))


def create_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "generate-all-configs", help="generate peer configuration files"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("wg0.json"),
        help="path of the config file",
    )
    parser.set_defaults(func=generate_all_configs)

    return parser
