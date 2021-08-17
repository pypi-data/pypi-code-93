from AsteriskRealtimeData.infrastructure.api.peer_controller import PeerController
from AsteriskRealtimeData.infrastructure.api.pause_reason_controller import (
    PauseReasonController,
)
from AsteriskRealtimeData.infrastructure.api.mascara_ipaddress_controller import (
    MascaraIpaddressController,
)
from AsteriskRealtimeData.infrastructure.api.queue_status_controller import QueueStatusController

def main():
    PauseReasonController().create({"pause_code": "1111", "description": "aaaaaaa"})
    PauseReasonController().create({"pause_code": "2222", "description": "bbbbbbb"})
    print(PauseReasonController().list())
    print(PauseReasonController().get_by_criteria("2222"))
    PauseReasonController().delete_by_criteria("2222")

    MascaraIpaddressController().create({"ipaddress": "1.1.1.1"})
    MascaraIpaddressController().create({"ipaddress": "2.2.2.2"})
    print(MascaraIpaddressController().list())
    print(MascaraIpaddressController().get_by_criteria("1.1.1.1"))
    MascaraIpaddressController().delete_by_criteria("2.2.2.2")

    PeerController().create(
        {"peer_name": "SIP/100", "peer_type": "SIP", "peer_ip_address": "1.1.1.1"}
    )
    PeerController().create(
        {"peer_name": "SIP/200", "peer_type": "SIP", "peer_ip_address": "2.2.2.2"}
    )
    print(PeerController().list())
    print(PeerController().get_by_criteria("SIP/100"))
    PeerController().delete_by_criteria("SIP/200")

    QueueStatusController().create({"status_code": "1", "description": "Estado de cola 1"})
    QueueStatusController().create({"status_code": "2", "description": "Estado de cola 2"})
    print(QueueStatusController().list())
    print(QueueStatusController().get_by_criteria("1"))
    QueueStatusController().delete_by_criteria("2")

if __name__ == "__main__":
    main()
