# -*- coding: utf-8 -*-
{
    'name': "TerraLab",

    'summary': """
        TerraLab System""",

    'description': """
        TerraLab extends Odoo by adding laboratory management functions.
    """,

    'author': "TerraLab Oy",
    'website': "https://www.terralab.fi",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Specific Industry Applications',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/sites.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
