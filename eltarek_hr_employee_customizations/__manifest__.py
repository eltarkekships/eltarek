# -*- coding: utf-8 -*-
{
    'name': "ElTarek HR Employee Customizations",

    'summary': """
    Module Employee for customizng adding fields and features in employee
    such social insurance and social insurance report,hiring details and so on
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Ahmed Abo El Fadl | Centione",
    'website': "http://www.centione.com",

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','account','analytic'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/social_insurance_wizard.xml',
        'views/hr_employee.xml',
        'views/social_insurance_config.xml',
        'views/hr_job.xml',
        'views/driver_line.xml',
        # 'views/driver_type_line.xml',
        'data/employee_sechdule_action.xml',

    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
