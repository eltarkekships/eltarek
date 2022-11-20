# -*- coding: utf-8 -*-
{
    'name': "ElTarek Over Time",

    'summary': """
    Module calculates employee overtime
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
    'depends': ['base',
                'hr',
                'project',
                'hr_payroll',
                'hr_contract',
                'eltarek_hr_payroll_base',
                'hr_work_entry_contract',
                'hr_attendance','eltarek_hr_self_service','eltarek_hr_public_holidays'],

    # always loaded
    'data': [
        'data/hr_payslip_input_type.xml',
        'data/salary_rules.xml',
        'views/over_time.xml',
        'views/over_time_configuration.xml',
        'security/ir.model.access.csv',
    ],

}
