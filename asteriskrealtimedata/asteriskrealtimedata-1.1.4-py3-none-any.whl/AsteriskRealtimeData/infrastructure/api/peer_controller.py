from typing import List
from AsteriskRealtimeData.domain.peer.peer_search_criteria_vo import PeerSearchCriteriaVo
from AsteriskRealtimeData.domain.peer.peer_update_vo import PeerUpdateVo
from AsteriskRealtimeData.application.peer_service import PeerService
from AsteriskRealtimeData.domain.peer.peer_vo import PeerVo


class PeerController:
    def create(self, peer_vo: PeerVo) -> PeerVo:
        return PeerService().create_peer(peer_vo)

    def update(self, peer_update_vo: PeerUpdateVo) -> PeerVo:
        return PeerService().update_peer(peer_update_vo)

    def get_all(self) -> List[PeerVo]:
        peers = PeerService().peer_list()
        result: list = []

        for peer in peers:
            result.append(peer)

        return result

    def get_by_peer(self, peer: str) -> PeerVo:
        return PeerService().get_peer(peer)

    def get_by_search_criteria(self, search_criteria: PeerSearchCriteriaVo) -> PeerVo:
        return PeerService().get_by_search_criteria(search_criteria)

    def delete_by_peer(self, peer: str) -> None:
        PeerService().delete_peer(peer)
