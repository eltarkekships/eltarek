# -*- coding: utf-8 -*-
{
    'name': "eltarek_existing_rfq",
    'depends': ['base', 'eltarek_delivery_request_generic', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ]
}