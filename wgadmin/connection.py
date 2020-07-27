from wgadmin import util

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wgadmin.peer import Peer


class Connection:
    def __init__(self, peer_a: "Peer", peer_b: "Peer", psk: str = ""):
        self.peer_a = peer_a
        self.peer_b = peer_b

        if psk:
            self.psk = psk
        else:
            self.psk = util.generate_psk()
