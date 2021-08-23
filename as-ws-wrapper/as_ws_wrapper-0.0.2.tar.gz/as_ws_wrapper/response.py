from zeep.xsd.valueobjects import CompoundValue


class ProcessedResponse:
    """
    Proxy para uma resposta processada do AccesstageSoapWrapper.

    Tem o intuito de padronizar a resposta recebida.
    """

    def __init__(self, response):
        self._response = response
        self.data = None
        self.data_type = None
        self._create_data()

    @property
    def original_data(self):
        """
        Informação original da resposta.

        :return: a resposta original
        """
        return self._response

    def _create_data(self):
        """
        Método para setar os atributos `data` e `data_type`.

        :return: N/A
        """
        if isinstance(self._response, list):
            self._create_list_data()
        elif isinstance(self._response, CompoundValue):
            self._create_entry_data(self._response)

    def _create_list_data(self):
        """
        Método para setar o data e data_type da
        resposta do tipo lista.

        :return: N/A
        """
        data = []
        sub_type = None
        for item in self._response:
            item_data, sub_type = self._create_entry_data(item, False)
            data.append(item_data)
        self.data = data
        self.data_type = f"list[{sub_type}]"

    def _create_entry_data(self, entry, set_data=True):
        """
        Método para setar/criar o data e data_type da
        resposta do tipo CompoundValue.

        :param entry: entrada CompoundValue a ser 'parseada'
        :param set_data: flag para controlar se o data e data_type devem ser setados em self  # noqa: E501
        :return: tupla com data e data_type
        """
        data = entry.__dict__["__values__"]
        data_type = type(entry).__name__
        if set_data:
            self.data = data
            self.data_type = data_type
        return data, data_type
