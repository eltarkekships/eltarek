# -*- coding: utf-8 -*-
{
    'name': "ElTarek HR Contract Customizations",

    'summary': """
    Module Contract for customizng adding fields and features in employee
        """,

    'author': "Ahmed Abo El Fadl | Centione",
    'website': "http://www.centione.com",

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_contract', 'hr_work_entry_contract_enterprise', 'hr_payroll',
                'eltarek_hr_payroll_base', 'hr_payroll_account', 'eltarek_hr_employee_customizations'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/contract_end_date_sechdule_action.xml',
        'data/social_insurance_salary_rule.xml',
        'views/hr_contract.xml',
        'views/hr_insurance_year.xml',
        'views/hr_payslip.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
