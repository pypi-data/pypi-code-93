from datetime import datetime
from asteriskinterfacelogger.logging import logger
from AsteriskRealtimeData.infrastructure.repositories.connection_interface import (
    Connection,
)

from AsteriskRealtimeData.domain.pause_reason.pause_reason import PauseReason
from AsteriskRealtimeData.domain.queue_status.queue_status import QueueStatus


class AsteriskInformations:
    database_connection: Connection

    def __init__(self, connection: Connection):
        self.database_connection = connection.get_connection()

    def insert_or_update_pause_reason(self, pause_reason: PauseReason):
        try:
            pause_reason_table = self._get_table_pause_reasons()
            return pause_reason_table.replace_one(
                {"pause_code": pause_reason.get_pause_code()},
                pause_reason.as_dict(),
                upsert=True,
            )
        except Exception as e:
            logger.error(
                {
                    "cause": "Can't add or update a pause reason",
                    "pause_code": pause_reason.get_pause_code(),
                    "description": pause_reason.get_description(),
                    "exception": e,
                }
            )

    def insert_or_update_queue_status(self, queue_status: QueueStatus):
        try:
            queue_status_table = self._get_table_queue_status()
            return queue_status_table.replace_one(
                {"status_code": queue_status.get_status_code()},
                queue_status.as_dict(),
                upsert=True,
            )
        except Exception as e:
            logger.error(
                {
                    "cause": "Can't add or update a queue status",
                    "pause_code": queue_status.get_status_code(),
                    "description": queue_status.get_description(),
                    "exception": e,
                }
            )

    def _get_table_pause_reasons(self):
        return self.database_connection.pause_reasons

    def _get_table_queue_status(self):
        return self.database_connection.queue_status

    def _get_table_peer(self):
        return self.database_connection.peers

    # def add_peer(self, peer: Peer):
    #     try:
    #         logger.info(
    #             {
    #                 "action": "Adding or updating a peer information",
    #                 "peer": peer.getPeerName(),
    #             }
    #         )
    #         self.database.peers.replace_one(
    #             {"peer": peer.getPeerName()}, peer.asDict(), upsert=True
    #         )
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't add or update a peer",
    #                 "peer": peer.getPeerName(),
    #                 "exception": e,
    #             }
    #         )

    # def add_mask_peer(self, mask_peer: MaskPeer):
    #     try:
    #         logger.info(
    #             {
    #                 "action": "Adding or updating a mask peer information",
    #                 "ipaddress": mask_peer.getPeerIpAddress(),
    #             }
    #         )
    #         self.database.mask_peers.replace_one(
    #             {"ipaddress": mask_peer.getPeerIpAddress()},
    #             mask_peer.asDict(),
    #             upsert=True,
    #         )
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't add or update a mask peer",
    #                 "peer": mask_peer.getPeerIpAddress(),
    #                 "exception": e,
    #             }
    #         )

    # def get_peer_by_peer_name(self, peer_name: str):
    #     try:
    #         logger.info(
    #             {"action": "Get peer information by peer name", "peer": peer_name}
    #         )
    #         result = self.database.peers.find_one({"peer": peer_name})
    #         return result
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't get peer information by peer name",
    #                 "peer": peer_name,
    #                 "exception": e,
    #             }
    #         )

    # def get_peer_by_ipaddress(self, ipaddress: str):
    #     try:
    #         logger.info(
    #             {"action": "Get peer information by ipaddress", "ipaddress": ipaddress}
    #         )
    #         result = self.database.peers.find_one({"ipaddress": ipaddress})
    #         return result
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't get peer information by ipaddress",
    #                 "ipaddress": ipaddress,
    #                 "exception": e,
    #             }
    #         )

    # def get_member_name_by_peer_name(self, peer_name: str):
    #     try:
    #         logger.info({"action": "Get member name by peer name", "peer": peer_name})
    #         result = self.database.queuemembers.find_one({"peer": peer_name})
    #         return result
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't get member name by peer name",
    #                 "peer": peer_name,
    #                 "exception": e,
    #             }
    #         )

    # def set_queuemember_status(self, peer_name: str, status_code: str):
    #     try:
    #         logger.info(
    #             {
    #                 "action": "Set the actual status for queuemember",
    #                 "queueMember": peer_name,
    #                 "status": status_code,
    #             }
    #         )
    #         new_status = {
    #             "peer": peer_name,
    #             "actual_status": status_code,
    #             "last_status_code": str(datetime.now()),
    #         }
    #         self.database.queuemembers.update_one(
    #             {"peer": peer_name}, {"$set": new_status}, upsert=True
    #         )
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't set the actual status for queuemember",
    #                 "queueMember": peer_name,
    #                 "status": status_code,
    #                 "exception": e,
    #             }
    #         )

    # def set_queuemember_peer(self, peer_name: str, member_name: str):
    #     try:
    #         logger.info(
    #             {
    #                 "action": "Set peer memberName pair",
    #                 "memberName": member_name,
    #                 "peer": peer_name,
    #             }
    #         )
    #         self.database.queuemembers.update_one(
    #             {"peer": peer_name},
    #             {"$set": {"peer": peer_name, "membername": member_name}},
    #             upsert=True,
    #         )
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't set peer memberName pair",
    #                 "memberName": member_name,
    #                 "peer": peer_name,
    #                 "exception": e,
    #             }
    #         )

    # def add_call_trackid(self, peer_name, trackid, dial_number, client_id):
    #     try:
    #         logger.info(
    #             {
    #                 "action": "Add trackid to originate call",
    #                 "peer_name": peer_name,
    #                 "trackid": trackid,
    #                 "dial_number": dial_number,
    #                 "client_id": client_id,
    #             }
    #         )
    #         originate_data = {
    #             "peer": peer_name,
    #             "trackid": trackid,
    #             "dialnumber": dial_number,
    #             "timestamp": str(datetime.now()),
    #             "clientid": client_id,
    #         }
    #         self.database.originate.delete_many({"peer": peer_name})
    #         self.database.originate.replace_one(
    #             {"peer": peer_name, "trackid": trackid}, originate_data, upsert=True
    #         )
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't set a trackid to call",
    #                 "data": str(originate_data),
    #                 "exception": e,
    #             }
    #         )

    # def get_call_trackid(self, peer_name):
    #     try:
    #         logger.info(
    #             {"action": "Get trackid from a originate call", "peer_name": peer_name}
    #         )
    #         result = self.database.originate.find_one({"peer": peer_name})
    #         return result
    #     except Exception as e:
    #         logger.error(
    #             {
    #                 "cause": "Can't get trackid for peer",
    #                 "peer": peer_name,
    #                 "exception": e,
    #             }
    #         )

    #     # def get_pause_cause_description(self, pause_code: str):
    #     #     agent_status = {
    #     #         "100001": "Conectado",
    #     #         "100002": "Disponible",
    #     #         "200001": "Desconectado",
    #     #         "200002": "En colación",
    #     #         "200003": "Baño",
    #     #         "200004": "En Reunión",
    #     #         "200005": "Atención vendedor",
    #     #         "300001": "Hablando",
    #     #         "300002": "ACW (After Call Work)",
    #     #         "300003": "Ocupado",
    #     #         "300004": "Recibiendo llamada",
    #     #         "300005": "Discando",
    #     #         "000000": "Estado desconocido",
    #     #     }
    #     # return agent_status[pause_code]

    # def is_paused(self, pause_code: str):
    #     return not pause_code.startswith("100")
