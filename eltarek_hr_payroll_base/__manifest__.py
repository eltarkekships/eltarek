# -*- coding: utf-8 -*-
{
    'name': "ELTarek HR Payroll Base",

    'summary': """
    Hr Payroll structure
        """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll', 'hr_work_entry'],

    # always loaded
    'data': [
        'data/hr_payroll_structure_type.xml',
        'data/hr_payroll_structure.xml',
    ],
}
