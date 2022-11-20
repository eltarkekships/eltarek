# -*- coding: utf-8 -*-
{
    'name': "ELTarek Hr Variable Allowance & Deduction",

    'summary': """
    module allowance and deuction for employee
        """,

    'description': """
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract', 'eltarek_hr_payroll_base','hr_work_entry_contract_enterprise'],

    # always loaded
    'data': [
        'views/hr_variable_allowance_deduction.xml',
        'views/hr_variable_allowance_deduction_type.xml',
        'security/ir.model.access.csv',
    ],
}