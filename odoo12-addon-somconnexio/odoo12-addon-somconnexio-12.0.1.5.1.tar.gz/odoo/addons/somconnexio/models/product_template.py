from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    private = fields.Boolean(
        string='Private',
        help='This field filters the products that we expose in the catalog API.',
        default=False)
