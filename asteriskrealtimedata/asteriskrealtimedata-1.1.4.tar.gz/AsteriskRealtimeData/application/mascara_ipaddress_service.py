from typing import List
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_search_criteria_vo import (
    MascaraIpaddressSearchCriteriaVo,
)
from antidote import inject, Provide
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_update_vo import MascaraIpaddressUpdateVo
from AsteriskRealtimeData.domain import pause_reason
from AsteriskRealtimeData.application.mascara_ipaddress_repository import MascaraIpaddressRepository
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress import MascaraIpaddress
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_vo import MascaraIpaddressVo


class MascaraIpaddressService:
    @inject
    def create_mascara_ipaddress(
        self, mascara_ipaddress_vo: MascaraIpaddressVo, repository: Provide[MascaraIpaddressRepository],
    ) -> MascaraIpaddressVo:

        mascara_ipaddress = MascaraIpaddress(
            ipaddress=mascara_ipaddress_vo.ipaddress, lastconnection=mascara_ipaddress_vo.lastconnection
        )

        repository.save(mascara_ipaddress, {"ipaddress": mascara_ipaddress_vo.ipaddress})

        return MascaraIpaddressVo(
            ipaddress=mascara_ipaddress_vo.ipaddress, lastconnection=mascara_ipaddress_vo.lastconnection
        )

    @inject
    def update_mascara_ipaddress(
        self, mascara_ipaddress_vo: MascaraIpaddressUpdateVo, repository: Provide[MascaraIpaddressRepository]
    ) -> MascaraIpaddressVo:

        repository.update(mascara_ipaddress_vo)

        mascara_ipaddress_dict = repository.get_by_criteria(mascara_ipaddress_vo.get_key_field())

        return MascaraIpaddressVo(
            ipaddress=mascara_ipaddress_dict["ipaddress"], lastconnection=mascara_ipaddress_dict["lastconnection"]
        )

    @inject()
    def mascara_ipaddress_list(self, repository: Provide[MascaraIpaddressRepository]) -> List[MascaraIpaddressVo]:
        result: list = []
        for document in repository.list():
            result.append(
                MascaraIpaddressVo(ipaddress=document["ipaddress"], lastconnection=document["lastconnection"])
            )
        return result

    @inject
    def get_mascara_ipaddress(
        self, ipaddress: str, repository: Provide[MascaraIpaddressRepository]
    ) -> MascaraIpaddressVo:
        mascara_ipaddress = repository.get_by_criteria({"ipaddress": ipaddress})
        return MascaraIpaddressVo(
            ipaddress=mascara_ipaddress["ipaddress"], lastconnection=mascara_ipaddress["lastconnection"]
        )

    @inject
    def get_by_search_criteria(
        self, search_criteria: MascaraIpaddressSearchCriteriaVo, repository: Provide[MascaraIpaddressRepository]
    ) -> MascaraIpaddressVo:
        mascara_ipaddress = repository.get_by_criteria(search_criteria.as_dict())
        return MascaraIpaddressVo(
            ipaddress=mascara_ipaddress["ipaddress"], lastconnection=mascara_ipaddress["lastconnection"]
        )

    @inject
    def delete_mascara_ipaddress(self, ipaddress: str, repository: Provide[MascaraIpaddressRepository]) -> None:
        repository.delete_by_criteria({"ipaddress": ipaddress})
