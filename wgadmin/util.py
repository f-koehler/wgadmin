import subprocess
import json
from typing import Tuple, Union, Any
from pathlib import Path


def generate_public_key(private_key: str) -> str:
    return (
        subprocess.check_output(["/usr/bin/wg", "pubkey"], input=private_key.encode())
        .decode()
        .strip()
    )


def generate_private_key() -> str:
    return subprocess.check_output(["/usr/bin/wg", "genkey"]).decode().strip()


def generate_keypair() -> Tuple[str, str]:
    private = generate_private_key()
    return private, generate_public_key(private)


def generate_psk() -> str:
    return subprocess.check_output(["/usr/bin/wg", "genpsk"]).decode().strip()


def load_config(path: Union[str, Path] = "config.json") -> Any:
    with open(path, "r") as fptr:
        return json.load(fptr)
