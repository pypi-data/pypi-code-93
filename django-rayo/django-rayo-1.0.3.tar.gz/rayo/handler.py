# -*- coding: utf-8 -*-
import logging

from requests import api

from rayo.connector import Connector, ConnectorException
from rayo.settings import api_settings

logger = logging.getLogger(__name__)


class RayoHandler:
    """
        Handler to send shipping payload to Rayo
    """

    def __init__(self, base_url=api_settings.RAYO['BASE_URL'],
                 user=api_settings.RAYO['USER'],
                 key=api_settings.RAYO['KEY'],
                 verify=True):

        self.base_url = base_url
        self.user = user
        self.key = key
        self.verify = verify
        self.connector = Connector(self._headers(), verify_ssl=self.verify)

    def _headers(self):
        """
            Here define the headers for all connections with Rayo.
        """
        return {
            'access-user': self.user,
            'access-key': self.key,
            'Content-Type': 'application/json',
        }

    def get_shipping_label(self):
        raise NotImplementedError(
            'get_shipping_label is not a method implemented for RayoHandler')

    def get_default_payload(self, instance):
        """
            This method generates by default all the necessary data with
            an appropriate structure for Rayo courier.
        """

        payload = {
            'has_pickup': 1,
            'has_delivery': 1,
            'auto_assignment': 0,
            'order_id': instance.reference,
            'tags': '',
            'id_store': api_settings.RAYO['STORE'],
            'pickups': [
                {
                    'address': api_settings.SENDER['CD_ADDRESS'],
                    'address2': '',
                    'comuna': api_settings.SENDER['CD_COMMUNE'],
                    'city': api_settings.SENDER['CD_CITY'],
                    'state': api_settings.SENDER['CD_STATE'],
                    'country': api_settings.SENDER['COUNTRY'],
                    'job_description': "Retiro Bodega",
                    'phone': '',
                    'name': f'Retiro de orden: {instance.reference}',
                    'metadata_name': api_settings.RAYO['METADATA_NAME'],
                    'metadata': {},
                    'email': '',
                }
            ],
            'deliveries': [
                {
                    'address': f'{instance.address.street} {instance.address.number}',
                    'address2': instance.address.unit,
                    'comuna': instance.commune.name,
                    'city': '',
                    'state': instance.region.name,
                    'country': api_settings.SENDER['COUNTRY'],
                    'job_description': f'Delivery Orden {instance.reference}',
                    'phone': instance.customer.phone,
                    'name': instance.customer.full_name,
                    'metadata_name': api_settings.RAYO['METADATA_NAME'],
                    'metadata': {}
                }
            ]
        }
        logger.debug(payload)
        return payload

    def create_shipping(self, data):
        """
            This method generate a Rayo shipping.
            If the get_default_payload method returns data, send it here,
            otherwise, generate your own payload.
        """

        url = f'{self.base_url}create_tasks'
        logger.debug(data)
        try:
            response = self.connector.post(url, data)
            if response.get('status') == 201:
                response.update({
                    'tracking_number': response['order_id'],
                    'tracking_url': response['deliveries'][0]['url_tracking_pickup'],
                })
                return response
            else:
                raise ConnectorException(response.get('message'), 'Error requesting create shipping', 500)

        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(error.message, error.description, error.code) from error

    def get_tracking(self, identifier):
        raise NotImplementedError(
            'get_tracking is not a method implemented for RayoHandler')

    def get_events(self, raw_data):
        """
            This method obtain array events.
            structure:
            {
                'tracking_number': 999999,
                'status': 'Exitoso',
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
                'status': 'Exitoso',
                'events': [{
                    'city': 'Santiago'
                    'state': 'RM',
                    'description': 'Llego al almacén',
                    'date': '12/12/2021'
                }]
            }

            status : ['No asignado', 'Asignado', 'Aceptado', 'Iniciado',
                       'En progreso', 'Exitoso', 'Fallido', 'Rechazado', 'Cancelado']
            response: ('Exitoso', True)
        """

        status = raw_data.get('status')
        is_delivered = False

        if status == 'Exitoso':
            is_delivered = True

        return status, is_delivered
