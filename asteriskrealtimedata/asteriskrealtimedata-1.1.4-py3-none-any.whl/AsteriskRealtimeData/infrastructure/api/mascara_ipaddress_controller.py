from typing import List
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_search_criteria_vo import (
    MascaraIpaddressSearchCriteriaVo,
)
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_update_vo import MascaraIpaddressUpdateVo
from AsteriskRealtimeData.application.mascara_ipaddress_service import MascaraIpaddressService
from AsteriskRealtimeData.domain.mascara_ipaddress.mascara_ipaddress_vo import MascaraIpaddressVo


class MascaraIpaddressController:
    def create(self, mascara_ipaddress_vo: MascaraIpaddressVo) -> MascaraIpaddressVo:
        return MascaraIpaddressService().create_mascara_ipaddress(mascara_ipaddress_vo)

    def update(self, mascara_ipaddress_vo: MascaraIpaddressUpdateVo) -> MascaraIpaddressVo:
        return MascaraIpaddressService().update_mascara_ipaddress(mascara_ipaddress_vo)

    def get_all(self) -> List[MascaraIpaddressVo]:
        mascara_ipaddresses = MascaraIpaddressService().mascara_ipaddress_list()
        result: list = []

        for mascara_ipaddress in mascara_ipaddresses:
            result.append(mascara_ipaddress)

        return result

    def get_by_ipaddress(self, ipaddress: str) -> MascaraIpaddressVo:
        return MascaraIpaddressService().get_mascara_ipaddress(ipaddress)

    def get_by_search_criteria(self, search_criteria: MascaraIpaddressSearchCriteriaVo) -> MascaraIpaddressVo:
        return MascaraIpaddressService().get_by_search_criteria(search_criteria)

    def delete_by_ipaddress(self, ipaddress: str) -> None:
        MascaraIpaddressService().delete_mascara_ipaddress(ipaddress)
