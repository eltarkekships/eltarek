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
    'depends': ['base','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'data/employee_sechdule_action.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}