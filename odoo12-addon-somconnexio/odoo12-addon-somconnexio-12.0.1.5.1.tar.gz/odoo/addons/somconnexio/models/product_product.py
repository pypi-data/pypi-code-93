from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'
    _sql_constraints = [
        ('default_code_uniq', 'unique (default_code)',
         'The product code must be unique !'
         ),
    ]

    custom_name = fields.Char(
        string='Custom name',
        translate=True,)

    showed_name = fields.Char(
        string='Name',
        compute='_compute_showed_name',
        translate=True,
        store=True,)

    discontinued = fields.Boolean(
        string='discontinued',
        default=False)

    @api.model
    def name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):

        if name:
            if args:
                new_args = [
                    '&', '|',
                    ('showed_name', operator, name), ('default_code', operator, name)
                ] + args
            else:
                new_args = [
                    '|',
                    ('showed_name', operator, name), ('default_code', operator, name)
                ]
            records = self.env['product.product'].search(new_args, limit=limit)
            return models.lazy_name_get(records)
        else:
            return super()._name_search(
                name=name, args=args, operator=operator,
                limit=limit, name_get_uid=name_get_uid
            )

    # TAKE IN MIND: We can overwrite this method from product_product for now,
    # but in the future we might need some additional features/conditions from
    # the original one:
    # https://github.com/odoo/odoo/blob/12.0/addons/product/models/product.py#L424
    @api.multi
    def name_get(self):
        data = []
        for product in self:
            data.append((product.id, product.showed_name))
        return data

    @api.depends('custom_name', 'name')
    def _compute_showed_name(self):
        for product in self:
            product.showed_name = product.custom_name or product.name
