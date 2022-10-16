# -*- coding: utf-8 -*-
{
    'name': "tarik_analytic_account_edit",
    'author': "Centione",
    'website': "",
    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/journal_item_analytic_account.xml',
        'views/hr_expense_analytic_account.xml',
    ],

}