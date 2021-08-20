# -*- coding: utf-8 -*-
import json
import urllib
import logging
from datetime import timedelta

from urbano.connector import Connector, ConnectorException
from urbano.settings import api_settings

logger = logging.getLogger(__name__)


class UrbanoHandler:
    """
        Handler to send shipping payload to Urbano
    """

    def __init__(self, base_url=api_settings.URBANO['BASE_URL'],
                 user=api_settings.URBANO['USER'],
                 password=api_settings.URBANO['PASSWORD'],
                 verify=True):

        self.base_url = base_url
        self.user = user
        self.password = password
        self.verify = verify
        self.connector = Connector(self._headers(), verify_ssl=self.verify)

    def _headers(self):
        """
            Here define the headers for all connections with Urbano.
        """
        return {
            'user': self.user,
            'pass': self.password,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def get_shipping_label(self):
        raise NotImplementedError(
            'get_shipping_label is not a method implemented for UrbanoHandler')

    def get_default_payload(self, instance):
        """
            This method generates by default all the necessary data with
            an appropriate structure for Urbano courier.
        """

        zone_code = instance.commune.zone_code

        if len(zone_code) == 4:
            zone_code = '0' + zone_code

        payload = {
            'anotacion': '',
            'arco_hor': '',
            'asegurado': '',
            'cedibles': [],
            'cod_barra': '',
            'cod_cliente': instance.customer.rut,
            'cod_rastreo': instance.reference,
            'correo_elec': '',
            'description': '',
            'dir_entrega': instance.address.full_address,
            'fech_emi_vent': instance.created_at,
            'fech_pro': instance.shipping_date,
            'fech_venc': instance.expiration_date,
            'id_contrato': api_settings.URBANO['ID_CONTRATO'],
            'id_direc': 0,
            'importe': '',
            'linea': '3',
            'mecanizado': 'NO',
            'med_pago': '',
            'moneda': 'CLP',
            'monto_asegurado': '',
            'nom_autorizado': instance.customer.full_name,
            'nom_autorizado_2': '',
            'nom_cliente': instance.customer.full_name,
            'nom_empresa': '',
            'nom_urb': '',
            'nro_doc_autorizado': instance.customer.rut,
            'nro_doc_autorizado_2': '',
            'nro_factura': '',
            'nro_guia_trans': instance.transport_guide_number,
            'nro_int': instance.address.unit,
            'nro_o_compra': instance.purchase_number,
            'nro_telf': '',
            'nro_telf_mobil': instance.customer.phone,
            'nro_via': instance.address.number,
            'peso_total': '',
            'picking': 'NO',
            'pieza_total': 1,
            'productos': [],
            'ref_direc': '',
            'sell_codigo': '',
            'sell_direcc': '',
            'sell_nombre': '',
            'sell_ubigeo': '',
            'ubi_direc': zone_code,
            'urgente': 'NO',
            'venta_seller': 'NO',
            'via_aereo': 'NO'
        }

        logger.debug(payload)
        return payload

    def create_shipping(self, data):
        """
            This method generate a Urbano shipping.
            If the get_default_payload method returns data, send it here,
            otherwise, generate your own payload.

            Additionally data was added to the response:
                tracking_number -> number to track the shipment.
        """
        try:
            params = {'json': json.dumps(data)}
            url = f'{self.base_url}ws/ue/ge/?{urllib.parse.urlencode(params)}'
            response = self.connector.get(url)
            logger.debug(response)

            if response.get('error') == 1:
                response.update({
                    'tracking_number': response['guia'],
                    'tracking_url': f"{api_settings.URBANO['TRACKING_BASE_URL']}{response['guia']}"
                })
                return response

            message_error = response.get(
                'mensaje') or response.get('msg_error')

            raise ConnectorException(
                message_error, 'Error requesting create shipping', 400
            )

        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(
                error.message, error.description, error.code) from error

    def get_tracking(self, identifier):
        """
            This method obtain a detail a shipping of Urbano.
        """
        try:
            data = {
                'guia': '',
                'docref': f'{identifier}',
                'vp_linea': '3'
            }
            params = {'json': json.dumps(data)}
            url = f'{self.base_url}ws/ue/tracking/?{urllib.parse.urlencode(params)}'
            response = self.connector.get(url)[0]
            logger.debug(response)

            if not response['sql_error'] == '1':
                raise ConnectorException(
                    response['msg_error'], 'Error requesting tracking', response['sql_error']
                )

            return response

        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(
                error.message, error.description, error.code) from error

    def get_events(self, raw_data):
        """
            This method obtain array events.
            structure:
            {
                'tracking_number': 999999,
                'status': 'Entregado',
                'events': [{
                    'city': 'Santiago',
                    'state': 'RM',
                    'description': 'Llego al almacén',
                    'date': '12/12/2021'
                }]
            }
            return [{
                'city': 'Santiago',
                'state': 'RM',
                'description': 'Llego al almacén',
                'date': '12/12/2021'
            }]
        """

        return raw_data.get('events')

    def get_status(self, raw_data):
        """
            This method returns the status of the order and "is_delivered".
            structure:
            {
                'tracking_number': 999999,
                'status': 'ENTREGADO',
                'events': [{
                    'city': 'Santiago'
                    'state': 'RM',
                    'description': 'Llego al almacén',
                    'date': '12/12/2021'
                }]
            }

            estatus : ['ADMITIDO', 'SALIO A RUTA', 'ENTREGADO', 'NO ENTREGADO']
            response: ('ENTREGADO', True)
        """

        status = raw_data.get('status')
        is_delivered = False

        if status == 'ENTREGADO':
            is_delivered = True

        return status, is_delivered
