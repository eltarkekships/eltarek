# -*- coding: utf-8 -*-
{
    'name': "El Tarek Purchase Agreement Payment",
    'author': "Centione",
    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase_requisition', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
