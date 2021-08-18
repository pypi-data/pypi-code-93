from typing import List
from AsteriskRealtimeData.domain.peer.peer_search_criteria_vo import PeerSearchCriteriaVo
from AsteriskRealtimeData.domain.peer.peer_update_vo import PeerUpdateVo
from antidote import inject, Provide
from AsteriskRealtimeData.application.peer_repository import PeerRepository
from AsteriskRealtimeData.domain.peer.peer import Peer
from AsteriskRealtimeData.domain.peer.peer_vo import PeerVo


class PeerService:
    @inject
    def create_peer(self, peer_vo: PeerVo, repository: Provide[PeerRepository],) -> PeerVo:

        peer = Peer(peer_name=peer_vo.peer_name, peer_type=peer_vo.peer_type, peer_ip_address=peer_vo.peer_ip_address,)

        repository.save(peer, {"peer_name": peer_vo.peer_name})

        return PeerVo(
            peer_name=peer_vo.peer_name, peer_type=peer_vo.peer_type, peer_ip_address=peer_vo.peer_ip_address,
        )

    @inject
    def update_peer(self, peer_update_vo: PeerUpdateVo, repository: Provide[PeerRepository]) -> PeerVo:
        repository.update(peer_update_vo)

        peer_dict = repository.get_by_criteria(peer_update_vo.get_key_field())

        return PeerVo(
            peer_name=peer_dict["peer_name"],
            peer_type=peer_dict["peer_type"],
            peer_ip_address=peer_dict["peer_ip_address"],
        )

    @inject()
    def peer_list(self, repository: Provide[PeerRepository]) -> List[PeerVo]:
        result: list = []
        print(repository)
        for document in repository.list():
            result.append(
                PeerVo(
                    peer_name=document["peer_name"],
                    peer_type=document["peer_type"],
                    peer_ip_address=document["peer_ip_address"],
                )
            )
        return result

    @inject
    def get_peer(self, peer_name: str, repository: Provide[PeerRepository]) -> PeerVo:
        peer = repository.get_by_criteria({"peer_name": peer_name})
        return PeerVo(
            peer_name=peer["peer_name"], peer_type=peer["peer_type"], peer_ip_address=peer["peer_ip_address"],
        )

    @inject
    def get_by_search_criteria(
        self, search_criteria: PeerSearchCriteriaVo, repository: Provide[PeerRepository]
    ) -> PeerVo:
        peer = repository.get_by_criteria(search_criteria.as_dict())
        return PeerVo(
            peer_name=peer["peer_name"], peer_type=peer["peer_type"], peer_ip_address=peer["peer_ip_address"],
        )

    @inject
    def delete_peer(self, peer_name: str, repository: Provide[PeerRepository]) -> None:
        repository.delete_by_criteria({"peer_name": peer_name})
