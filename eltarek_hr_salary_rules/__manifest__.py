# -*- coding: utf-8 -*-
{
    'name': "ElTarek HR Salary Rules",

    'summary': """
    Module slary rules for customizng employee salaries
        """,

    'author': "Ahmed Abo El Fadl | Centione",
    'website': "http://www.centione.com",

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract',  'hr_payroll',
                'eltarek_hr_payroll_base', 'hr_payroll_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/salary_rules.xml',
        'views/hr_salary_rule.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
