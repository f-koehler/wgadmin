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

import json
import subprocess
from pathlib import Path
from typing import Any, Tuple, Union


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
