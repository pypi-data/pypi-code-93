# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_telecom = fields.Boolean(string="Is Telecom order?")

    product_id = fields.Many2one(
        "product.product",
        computed='_compute_product',
        string="Product"
    )

    def _compute_product(self):
        for order in self:
            if order.order_line:
                order.product_id = order.order_line[0].product_id
