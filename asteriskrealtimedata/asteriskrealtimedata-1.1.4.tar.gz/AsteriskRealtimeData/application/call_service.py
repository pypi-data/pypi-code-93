from typing import List
from AsteriskRealtimeData.domain.call.call_search_criteria_vo import CallSerchCriteriaVo
from AsteriskRealtimeData.domain.call.call_update_vo import CallUpdateVo
from antidote import inject, Provide
from AsteriskRealtimeData.application.call_repository import CallRepository
from AsteriskRealtimeData.domain.call.call import Call
from AsteriskRealtimeData.domain.call.call_vo import CallVo


class CallService:
    @inject
    def create_call(self, call_vo: CallVo, repository: Provide[CallRepository],) -> CallVo:

        call = Call(
            peer_name=call_vo.peer_name,
            client_id=call_vo.client_id,
            dialnumber=call_vo.dialnumber,
            lastevent=call_vo.lastevent,
            track_id=call_vo.track_id,
            call_linkedid=call_vo.call_linkedid,
            call_actor_address=call_vo.call_actor_address,
            event_name=call_vo.event_name,
            origin_channel=call_vo.origin_channel,
            destination_channel=call_vo.destination_channel,
            origin_number=call_vo.origin_number,
            destination_number=call_vo.destination_number,
        )

        repository.save(call, {"call_linkedid": call_vo.call_linkedid})

        return CallVo(
            peer_name=call_vo.peer_name,
            client_id=call_vo.client_id,
            dialnumber=call_vo.dialnumber,
            lastevent=call_vo.lastevent,
            track_id=call_vo.track_id,
            call_linkedid=call_vo.call_linkedid,
            call_actor_address=call_vo.call_actor_address,
            event_name=call_vo.event_name,
            origin_channel=call_vo.origin_channel,
            destination_channel=call_vo.destination_channel,
            origin_number=call_vo.origin_number,
            destination_number=call_vo.destination_number,
        )

    @inject
    def update_call(self, call_update_vo: CallUpdateVo, repository: Provide[CallRepository]) -> CallVo:

        repository.update(call_update_vo)

        call_dict = repository.get_by_criteria(call_update_vo.get_key_field())

        return CallVo(
            peer_name=call_dict["peer_name"],
            client_id=call_dict["client_id"],
            dialnumber=call_dict["dialnumber"],
            lastevent=call_dict["lastevent"],
            track_id=call_dict["track_id"],
            call_linkedid=call_dict["call_linkedid"],
            call_actor_address=call_dict["call_actor_address"],
            event_name=call_dict["event_name"],
            origin_channel=call_dict["origin_channel"],
            destination_channel=call_dict["destination_channel"],
            origin_number=call_dict["origin_number"],
            destination_number=call_dict["destination_number"],
        )

    @inject()
    def call_list(self, repository: Provide[CallRepository]) -> List[CallVo]:
        result: list = []
        for document in repository.list():
            result.append(
                CallVo(
                    peer_name=document["peer_name"],
                    client_id=document["client_id"],
                    dialnumber=document["dialnumber"],
                    lastevent=document["lastevent"],
                    track_id=document["track_id"],
                    call_linkedid=document["call_linkedid"],
                    call_actor_address=document["call_actor_address"],
                    event_name=document["event_name"],
                    origin_channel=document["origin_channel"],
                    destination_channel=document["destination_channel"],
                    origin_number=document["origin_number"],
                    destination_number=document["destination_number"],
                )
            )
        return result

    @inject
    def get_call(self, call_linkedid: str, repository: Provide[CallRepository]) -> CallVo:

        call = repository.get_by_criteria({"call_linkedid": call_linkedid})
        return CallVo(
            peer_name=call["peer_name"],
            client_id=call["client_id"],
            dialnumber=call["dialnumber"],
            lastevent=call["lastevent"],
            track_id=call["track_id"],
            call_linkedid=call["call_linkedid"],
            call_actor_address=call["call_actor_address"],
            event_name=call["event_name"],
            origin_channel=call["origin_channel"],
            destination_channel=call["destination_channel"],
            origin_number=call["origin_number"],
            destination_number=call["destination_number"],
        )

    @inject
    def get_by_search_criteria(
        self, search_criteria: CallSerchCriteriaVo, repository: Provide[CallRepository]
    ) -> CallVo:
        call = repository.get_by_criteria(search_criteria.as_dict())
        return CallVo(
            peer_name=call["peer_name"],
            client_id=call["client_id"],
            dialnumber=call["dialnumber"],
            lastevent=call["lastevent"],
            track_id=call["track_id"],
            call_linkedid=call["call_linkedid"],
            call_actor_address=call["call_actor_address"],
            event_name=call["event_name"],
            origin_channel=call["origin_channel"],
            destination_channel=call["destination_channel"],
            origin_number=call["origin_number"],
            destination_number=call["destination_number"],
        )

    @inject
    def delete_call(self, call_linkedid: str, repository: Provide[CallRepository]) -> None:
        repository.delete_by_criteria({"call_linkedid": call_linkedid})
