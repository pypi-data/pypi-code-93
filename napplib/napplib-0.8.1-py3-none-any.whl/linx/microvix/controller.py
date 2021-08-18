import requests, json, logging
from .models.authentication import MicrovixAuthentication
from .utils import xml_to_dict_array
from datetime import datetime
import copy

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(threadName)-11s %(levelname)-10s %(message)s")


class MicrovixController:

	url = 'http://webapi.microvix.com.br/1.0/api/integracao'

	@classmethod
	def get_stocks(self, authentication, start_mov_date= None, end_mov_date=None):

		logging.info(f"Getting stocks info...")

		authentication = authentication.copy()

		authentication.setCommandName('LinxProdutosDetalhes')

		if start_mov_date and isinstance(start_mov_date, datetime):
			start_mov_date = start_mov_date.strftime('%Y-%m-%d')

		authentication.data_mov_ini = start_mov_date

		if end_mov_date and isinstance(end_mov_date, datetime):
			end_mov_date = end_mov_date.strftime('%Y-%m-%d')

		authentication.data_mov_fim = end_mov_date

		return self.__post(authentication)


	@classmethod
	def get_product_attributes(self, authentication, start_mov_date= None, end_mov_date=None, product_code=None):

		logging.info(f"Getting  info...")

		authentication = authentication.copy()

		authentication.setCommandName('LinxProdutosCamposAdicionais')

		if start_mov_date and isinstance(start_mov_date, datetime):
			start_mov_date = start_mov_date.strftime('%Y-%m-%d')

		authentication.data_mov_ini = start_mov_date

		if end_mov_date and isinstance(end_mov_date, datetime):
			end_mov_date = end_mov_date.strftime('%Y-%m-%d')

		authentication.data_mov_fim = end_mov_date

		authentication.cod_produto = product_code

		return self.__post(authentication)


	@classmethod
	def get_products(self, authentication, start_update_date=None, end_update_date=None, product_code=None):

		logging.info(f"Getting products...")

		authentication = authentication.copy()

		authentication.setCommandName('LinxProdutos')

		if start_update_date and isinstance(start_update_date, datetime):
			start_update_date = start_update_date.strftime('%Y-%m-%d')

		authentication.dt_update_inicio = start_update_date

		if end_update_date and isinstance(start_update_date, datetime):
			end_update_date = end_update_date.strftime('%Y-%m-%d')

		authentication.dt_update_fim = end_update_date

		authentication.cod_produto = product_code

		return self.__post(authentication)


	def __post(authentication):

		payload = str(authentication)

		headers = { 'Content-Type': 'application/xml' }

		r = requests.post(MicrovixController.url, headers=headers, data=payload)

		if not r:
			raise Exception('Request returned nothing', authentication)

		return xml_to_dict_array(r.content)
