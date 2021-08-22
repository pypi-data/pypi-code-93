import logging
import uuid
from typing import Optional

import aiohttp
import simplejson as m_json

from .conf import MONETA_HOST
from .models import (
    CreateAccountRequest,
    CreateProfileRequest,
    Envelope,
    FindAccountByIdRequest,
    FindOperationsListByCTIDRequest,
    FindProfileInfoRequest,
    GetNextStepRequest,
    GetOperationDetailsByIdRequest,
    InvoiceRequest,
    Method,
    PaymentRequest,
    RefundRequest,
    Request,
    Response,
    VerifyPaymentRequest,
)
import decoders


MONETA_HOST_FULL = f'https://{MONETA_HOST}/services'
POST = 'POST'
GET = 'GET'


logger = logging.getLogger('my_logger')


class Client:
    def __init__(
        self,
        username: str,
        password: str,
        host: str = MONETA_HOST_FULL,
        session: Optional[aiohttp.ClientSession] = None,
        sale_point_username: Optional[str] = None,
        sale_point_password: Optional[str] = None,
    ):
        self._url = host
        self._username: str = username
        self._password: str = password
        self._sale_point_username: Optional[str] = sale_point_username
        self._sale_point_password: Optional[str] = sale_point_password
        if session:
            self._session: Optional[aiohttp.ClientSession] = session
        else:
            self._session = aiohttp.ClientSession()

    async def create_profile(self, phone: str, unit_id: int) -> int:
        return await self._moneta_request(
            method=CreateProfileRequest.make_anon_profile(unit_id=unit_id, phone=phone)
        )

    async def create_account(self, alias: str, unit_id: int, payment_password: str) -> int:
        return await self._moneta_request(
            method=CreateAccountRequest(alias=alias, unitId=unit_id, paymentPassword=payment_password)
        )

    async def get_bank_info(self):
        return await self._moneta_request(method=GetNextStepRequest.get_bank_info())

    async def create_invoice(self, payee: int, amount: str, trans_id: str, bank_id: str):
        return await self._moneta_request(
            method=InvoiceRequest.invoice(
                payee=payee, amount=amount, trans_id=trans_id, bank_id=bank_id
            )
        )

    async def get_operation_details_by_id(self, operation_id):
        return await self._moneta_request(
            method=GetOperationDetailsByIdRequest(value=operation_id)
        )

    async def find_profile_info(self, phone: str) -> Response:
        return await self._moneta_request(
            method=FindProfileInfoRequest.by_phone(phone=phone)
        )

    async def get_operation_details_by_ctid(
        self, account_id: int, ctid: str, use_sale_point_auth: bool = False,
    ) -> Response:
        return await self._moneta_request(
            method=FindOperationsListByCTIDRequest(
                accountId=account_id, clientTransaction=ctid
            ),
            use_sale_point_auth=use_sale_point_auth
        )

    async def find_account_by_id(self, account_id: int) -> Response:
        return await self._moneta_request(
            method=FindAccountByIdRequest(value=account_id)
        )

    async def verify_payment_request(
        self,
        payee: int,
        payer: int,
        amount: str,
        is_payer_amount: bool,
        payment_password: str,
        client_transaction: str,
    ) -> Response:
        return await self._moneta_request(
            method=VerifyPaymentRequest(
                payee=payee,
                payer=payer,
                amount=str(amount),
                isPayerAmount=is_payer_amount,
                paymentPassword=payment_password,
                clientTransaction=client_transaction
            )
        )

    async def payment_request(
        self,
        payee: int,
        payer: int,
        amount: str,
        is_payer_amount: bool,
        payment_password: str,
        client_transaction: str,
    ) -> Response:
        return await self._moneta_request(
            method=PaymentRequest(
                payee=payee,
                payer=payer,
                amount=amount,
                isPayerAmount=is_payer_amount,
                paymentPassword=payment_password,
                clientTransaction=client_transaction
            )
        )

    async def refund_request(
            self,
            transaction_id: int,
            amount: str,
            paymentPassword: Optional[str] = None,
            clientTransaction: Optional[str] = None
    ) -> Response:
        return await self._moneta_request(
            method=RefundRequest(
                transactionId=transaction_id,
                amount=amount,
                paymentPassword=paymentPassword,
                clientTransaction=clientTransaction
            ),
            use_sale_point_auth=True,
        )

    async def _moneta_request(
        self,
        method: Method,
        use_sale_point_auth: bool = False
    ) -> Response:
        if use_sale_point_auth:
            username = self._sale_point_username
            password = self._sale_point_password
        else:
            username = self._username
            password = self._password
        raw_res = await self._base_request(
            method=POST,
            json=Request(
                Envelope=Envelope.make_auth_method(
                    method=method,
                    username=username,
                    password=password,
                )
            ).asdict()
        )
        res = Response.from_dict(raw_res)
        if res.is_error:
            e_type, e_msg, e_code = res.error_detail()
            if e_code not in ['500.3.2.31', '500.3.2.36', '500.3.1.18']:
                logger.error(res.error_detail())
                raise ValueError(res.error_detail())
            else:
                logger.warning(res.error_detail())
        return res

    async def _base_request(
        self,
        method: Optional[str] = None,
        *,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> aiohttp.ClientResponse:
        if method is None and json is not None:
            method = POST
        elif method is None:
            method = GET

        if headers is None:
            headers = {}

        request_id = uuid.uuid4().hex
        logger.info('[%s] json %s', request_id, json)
        logger.info('[%s] Request to moneta url=%s, json=%s', request_id, self._url, m_json.dumps(
            json, indent=4, cls=decoders.DecimalEncoder
        ))
        if method == POST:
            res = await self._session.post(
                url=self._url,
                json=json,
                headers={'Content-Type': 'application/json;charset=UTF-8', **headers}
            )
        else:
            res = await self._session.get(self.url, headers=headers)

        json = await res.json()
        logger.info(
            '[%s] Response from moneta status_code=%s, json=%s',
            request_id,
            res.status,
            m_json.dumps(json, indent=4)
        )

        return json
