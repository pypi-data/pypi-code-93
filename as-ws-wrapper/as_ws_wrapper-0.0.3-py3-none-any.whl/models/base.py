from typing import Literal, Optional, Union

from pydantic import BaseModel, constr


class PayerInfo(BaseModel):
    payer_document: constr(min_length=14, max_length=14)  # CPF/CNPJ do pagador
    payer_document_type: Literal[
        "CPF", "CNPJ"
    ]  # tipo do documento 'CPF' ou 'CNPJ' do pagador
    payer_name: str  # nome do pagador
    payer_bank_account_number: str  # número da conta bancária do pagador  | TED/DOC apenas  # noqa: E501
    payer_bank_account_number_dv: str  # dv do númerp da conta bancária do pagador  | TED/DOC apenas  # noqa: E501
    payer_bank_account_routing: str  # agência da conta bancária do pagador  | TED/DOC apenas  # noqa: E501
    payer_bank_account_routing_dv: str  # dv da agência da conta bancária do pagador  | TED/DOC apenas  # noqa: E501
    payer_convenio: str  # convênio do pagador


class ReceiverInfo(BaseModel):
    """
    Informações do favorecido/beneficiário
    """

    receiver_document: constr(min_length=14, max_length=14)  # CPF/CNPJ do recebedor
    receiver_document_type: Literal[
        "CPF", "CNPJ"
    ]  # tipo do documento 'CPF' ou 'CNPJ' recebedor
    receiver_name: str  # nome do recebedor

    receiver_bank_account_bank_name: Optional[
        str
    ]  # nome do banco da conta bancária do recebedor  | TED/DOC apenas
    receiver_bank_account_bank_code: Optional[
        Union[constr(min_length=3, max_length=3), constr(min_length=0, max_length=0)]
    ]  # código do banco da conta bancária do recebedor  | TED/DOC apenas
    receiver_bank_account_number: Optional[
        str
    ]  # número da conta bancária do recebedor  | TED/DOC apenas
    receiver_bank_account_number_dv: Optional[
        str
    ]  # dv do númerp da conta bancária do recebedor  | TED/DOC apenas
    receiver_bank_account_routing: Optional[
        str
    ]  # agência da conta bancária do recebedor  | TED/DOC apenas
    receiver_bank_account_routing_dv: Optional[
        str
    ]  # dv da agência da conta bancária do recebedor  | TED/DOC apenas
    receiver_bank_account_routing_number_dv: Optional[
        Union[str, None]
    ]  # dv do agência/número da conta bancária do recebedor  | TED/DOC apenas


class TransactionModel(ReceiverInfo, PayerInfo, BaseModel):
    """
    Informações da transação de pagamento
    """

    """ HEADER DO LOTE """

    payment_type: Literal[
        "01", "03", "41", "43", "30", "31"
    ]  # código do tipo de pagamento

    """ SEGMENTO A + B (DOC/TED) + J + J52 (boleto) """
    number: constr(max_length=20)  # Numeração única e alfanumérica
    payment_amount: int  # quantia paga em centavos
    payment_date: str  # data de pagamento (formato DDMMAAAA)
    code_line: Optional[str]  # linha digitável do boleto  | boleto apenas
    expiration_date: Optional[
        str
    ]  # data do vencimento (formato DDMMAAAA)  | boleto apenas
