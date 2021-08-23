# -*- coding: utf-8 -*-
{
    'name': "Vertical Telecom",
    'summary': """""",
    'description': """""",
    'author': "Coopdevs Treball SCCL",
    'website': 'https://coopdevs.org',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Telecom flows management',
    'version': '12.0.0.0.1',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'component_event',
        'crm',
        'crm_lead_product',
        'product',
        'sale',
        'sale_management',
        'sale_substate',
    ],
    # always loaded
    'data': [
        # Module Data
        'data/ir_module_category.xml',
        # Security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # Data
        'data/previous.provider.csv',
        'data/product_attribute.xml',
        'data/product_categories.xml',
        'data/service_supplier.xml',
        'data/service_technology.xml',
        # Views
        'views/crm_lead.xml',
        'views/product.xml',
        'views/sale_order.xml',
        # Menu
        'views/menu.xml',
        # Wizards
        'wizards/crm_lead_line_creation/crm_lead_line_creation_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
