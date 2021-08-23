from datetime import datetime

from zeep.exceptions import TransportError
from zeep.xsd.valueobjects import CompoundValue

from ..response import ProcessedResponse
from .soap import BaseSoapWrapper


class AccesstageSoapWrapper(BaseSoapWrapper):
    """
    Wrapper dos webservices da Accesstage.
    """

    ACCESSTAGE_BASE_WSL = "https://www.accesstage.com.br/ASTrafegoWS/ProxyServices/"

    def _process_response(self, response):
        """
        Método para proessar uma resposta.

        :param response: resposta a ser processada
        :return: resposta processada (ProcessedResponse)
        """
        self._raise_for_status(response)
        processed_response = ProcessedResponse(response)
        return processed_response

    def _raise_for_status(self, response):
        """
        Método para identificar erros do resquest/response.

        :raises TransportError: levanta exceção na identificação de erros.

        :param response: resposta a ser processada
        :return: N/A
        """
        try:
            if isinstance(response, CompoundValue) and response["dscErroEnvio"]:
                raise TransportError(message=response["dscErroEnvio"], content=response)
        except KeyError:
            pass
        try:
            if isinstance(response, CompoundValue):
                if any(
                    value in response["dscStatusRetirada"]
                    for value in ["Erro", "invalidVariables"]
                ):
                    raise TransportError(
                        message=response["dscStatusRetirada"], content=response
                    )
        except KeyError:
            pass

    def _get_wsl(self, service):
        """
        Método para retornar o 'url' do webservice a ser utilizado.

        :param service: webservice a ser utilizado
        :return: string do wsl
        """
        return f"{self.ACCESSTAGE_BASE_WSL}{service}?wsdl"

    def lista_servicos(self):
        """
        Método para listar os serviços disponiveis.

        Cada serviço nesse caso é um tipo de comunicação.
        Por exemplo, pode ser o extrato da conta bancária ou
        realização de alguma transação.

        Cada serviço possui seu identificador (codigoIntercambio) único.

        :return: resposta processada com lista de serviços
        """
        client = self.get_client(wsdl=self._get_wsl("ListaServicosDisponiveisProxy"))

        r = client.service.process()

        r = self._process_response(r)

        return r

    def lista_mensagens(self):
        """
        Método para listar as mensagens disponíveis.

        Cada mensagem é referente à algum tipo de serviço
        e possui o seu identificador (trkIdIn) único.

        :return: resposta processada com lista de mensagens
        """
        client = self.get_client(wsdl=self._get_wsl("ListaMsgDisponiveisProxy"))

        r = client.service.process()

        r = self._process_response(r)

        return r

    def envia_mensagem(
        self, cod_intercambio: str, flag_compactacao: bool, msg_b64_bytes: bytes
    ):
        """
        Método para enviar uma mensagem.

        Cada mensagem é referente à algum tipo de serviço.

        :param cod_intercambio: identificador do serviço
        :param flag_compactacao: flag de compactação
        :param msg_b64_bytes: mensagem em bytes base 64
        :return: resposta processada com status do envio
        """
        client = self.get_client(wsdl=self._get_wsl("EnvioMensagemProxy"))

        data = dict(
            codIntercambio=cod_intercambio,
            flgCompactacao=flag_compactacao,
            dscConteudoMensagem=msg_b64_bytes,
        )

        r = client.service.process(**data)

        r = self._process_response(r)

        return r

    def recupera_mensagem(self, identifier):
        """
        Método para recuperar as informações de
        uma mensagem da lista de mensagens.

        :param identifier: identificador único da mensagem (trkIdIn)
        :return: resposta processada com dados da mensagem
        """
        client = self.get_client(wsdl=self._get_wsl("RecuperacaoMensagemProxy"))

        data = dict(trackingId=identifier)

        r = client.service.process(**data)

        r = self._process_response(r)

        return r

    def confirma_retirada(self, identifier, file_name, datetime_retrieval=None):
        """
        Método para retirar a mensagem da lista de mensagens.

        :param identifier: identificador único da mensagem (trkIdIn)
        :param datetime_retrieval: data e hora da retirada
        :param file_name: ????
        :return: resposta proessada com status da retirada
        """
        client = self.get_client(wsdl=self._get_wsl("ConfirmacaoRetiradaProxy"))

        if datetime_retrieval is None:
            datetime_retrieval = datetime.now().isoformat()

        data = dict(
            trackingID=identifier, dataRetirada=datetime_retrieval, nmeArquivo=file_name
        )

        r = client.service.process(**data)

        r = self._process_response(r)

        return r
