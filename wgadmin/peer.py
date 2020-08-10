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

from __future__ import annotations

from typing import List, Optional

from wgadmin import util
from wgadmin.connection import Connection


class Peer:
    def __init__(
        self,
        name: str,
        interface: str = "wg0",
        ipv4: str = "",
        ipv6: str = "",
        port: int = 51902,
        private_key: Optional[str] = None,
        public_key: Optional[str] = None,
        endpoint_address: str = "",
    ):
        self.name = name
        self.interface = interface
        self.address_ipv4 = ipv4
        self.address_ipv6 = ipv6
        self.port = port

        if private_key:
            self.private_key = private_key
        else:
            self.private_key = util.generate_private_key()

        if public_key:
            self.public_key = public_key
        else:
            self.public_key = util.generate_public_key(self.private_key)

        self.endpoint_address = endpoint_address

        self.connections: List[Connection] = []

    def add_connection(self, peer_b: Peer, psk: str = ""):
        connection = Connection(self, peer_b, psk)
        self.connections.append(connection)

        peer_b.connections.append(Connection(peer_b, self, connection.psk))
