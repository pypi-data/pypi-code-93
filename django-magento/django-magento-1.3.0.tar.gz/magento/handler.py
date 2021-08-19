# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta

from django.utils import timezone

from magento.connector import Connector, ConnectorException
from magento.settings import api_settings

logger = logging.getLogger(__name__)


class MagentoHandler:
    """
        Handler to connect with Magento
    """
    def __init__(self, base_url=api_settings.MAGENTO['BASE_URL'],
                 api_key=api_settings.MAGENTO['API_KEY'],
                 verify=True):

        self.base_url = base_url
        self.api_key = api_key
        self.verify = verify
        self.connector = Connector(self._headers(), verify_ssl=self.verify)

    def _headers(self):
        """
            Here define the headers for all connections with Magento.
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'cache-control': 'no-cache',
        }

    def get_orders(self, params={}):
        """
            Here it makes a request to magento to obtain all orders with default filter.
            status = 'complete', but receive params for any valid filter in magento.
        """

        default_params = {
            'searchCriteria[filterGroups][0][filters][0][field]': 'status',
            'searchCriteria[filterGroups][0][filters][0][value]': 'complete'
        }
        default_params.update(params)

        url = f'{self.base_url}V1/orders'

        logger.debug(params)
        try:
            response = self.connector.get(url, default_params)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def get_order_detail(self, identifier):
        """
        Here it a makes a request to magento to obtain order detail.
        """
        url = f'{self.base_url}V1/orders/{identifier}'

        try:
            response = self.connector.get(url)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def get_order_products(self, identifier):
        """
        Here it a makes a request to magento to obtain order detail but only
        with the items to ship.

        return:
        {
            "items": [
                {
                    "item_id": 140,
                    "qty_ordered": 1,
                    "sku": "ALCNHDA01B57Z"
                }
            ]
        }
        """
        params = {'fields': 'items[qty_ordered,sku,item_id]'}
        url = f'{self.base_url}V1/orders/{identifier}'
        logger.debug(params)

        try:
            response = self.connector.get(url, params)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def create_shipment(self, identifier, items):
        """
        Endpoint calling order ship, this adds the items
        to a shipment to substract the used stock

        Arguments:
        - identity -> Magento order id
        - items -> list with dictionary containing order_item_id and qty
        - items = [{'order_item_id': 9999, 'qty': 1}]

        Return: 999 -> ID Shipment
        """
        payload = {
            'items': [
                {
                    'order_item_id': item['order_item_id'],
                    'qty': item['qty']
                } for item in items
            ],
            'notify': False,
            'appendComment': False
        }

        url = f'{self.base_url}V1/order/{identifier}/ship'

        logger.debug(payload)
        try:
            response = self.connector.post(url, payload)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def get_invoice(self, order_id):
        """
        Makes a request to magento to get invoice filtering by order_id.
        """
        default_params = {
            'searchCriteria[filter_groups][0][filters][0][field]': 'order_id',
            'searchCriteriasearchCriteria[filter_groups][0][filters][0][condition_type]': 'eq',
            'searchCriteria[filter_groups][0][filters][0][value]': f'{order_id}'
        }

        url = f'{self.base_url}V1/invoices'

        logger.debug(default_params)
        try:
            response = self.connector.get(url, default_params)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def get_creditmemo(self, creditmemo_id):
        """
        Makes a request to magento to get credit memo info.
        """
        default_params = {
            'searchCriteria': ''
        }

        url = f'{self.base_url}V1/creditmemo/{creditmemo_id}'

        logger.debug(url)
        try:
            response = self.connector.get(url, default_params)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def get_item_creditmemo_payload(self, product, quantity):
        """
            This method generates payload of items to be inserted in credit memo data
        """
        payload = {
            'order_item_id': product,
            'qty': quantity
        }
        logger.debug(payload)
        return payload

    def get_creditmemo_default_payload(self, instance):
        """
            This method validates data that was previously converted to instance before sending it to magento.
        """
        payload_items = [
            {
                'order_item_id': item.order_item_id,
                'qty': item.qty
            } for item in instance.items
        ]

        payload = {
            'items': payload_items,
            'notify': instance.notify,
            'arguments': {
                'shipping_amount': instance.arguments.shipping_amount,
                'adjustment_positive': instance.arguments.adjustment_positive,
                'adjustment_negative': instance.arguments.adjustment_negative,
                'extension_attributes': {
                    'return_to_stock_items': instance.arguments.extension_attributes.return_to_stock_items
                },
            },
        }
        logger.debug(payload)
        return payload

    def online_refund(self, invoice_id, data):
        """
        Endpoint to create a creditmemo or refund to an invoice.
        """

        url = f'{self.base_url}V1/invoice/{invoice_id}/refund'
        try:
            response = self.connector.post(url, data, f'Invoice {invoice_id} refund')
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def create_invoice(self, identifier, items):
        """
        Endpoint calling order invoice, this adds the items
        to a invoice and completes the order

        Arguments:
        - identifier -> Magento order id
        - items -> list with dictionary containing order_item_id and qty
        - items = [{'order_item_id': 9999, 'qty': 1}]

        Return: 999 -> ID Invoice
        """
        payload = {
            'items': [
                {
                    'order_item_id': item['order_item_id'],
                    'qty': item['qty']
                } for item in items
            ],
            'notify': False,
            'appendComment': False
        }

        url = f'{self.base_url}V1/order/{identifier}/invoice'

        logger.debug(payload)
        try:
            response = self.connector.post(url, payload)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def update_order(self, identifier, comment, status, notify_customer=True):
        """
        Endpoint calling order comment, with this endpoint a comment can be added
        to the order.

        Arguments:
        - identifier -> Magento order id
        - comment -> String with the comment
        - notify_customer -> Boolean to set notify by email to the customer

        Return: True
        """
        payload = {
            'statusHistory': {
                'comment': comment,
                'created_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_customer_notified': 1 if notify_customer else 0,
                'is_visible_on_front': 1 if notify_customer else 0,
                'status': status,
                'extension_attributes': {}
            }
        }
        url = f'{self.base_url}V1/orders/{identifier}/comments'

        logger.debug(payload)
        try:
            response = self.connector.post(url, payload)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False

    def cancel_order(self, identifier):
        """
        Endpoint calling order cancel, this calling cancels the order
        Arguments:

        - identifier -> Magento order id

        Return: True
        """
        payload = {}
        url = f'{self.base_url}V1/orders/{identifier}/cancel'

        logger.debug(payload)
        try:
            response = self.connector.post(url, payload)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            return False
