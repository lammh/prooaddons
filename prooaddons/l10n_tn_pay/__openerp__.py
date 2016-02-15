{
    'name': 'HR tn pay',
    'version': '1.0',
    'author': 'ProoSoft',
    'category': 'Human Resources',
    'sequence': 1,
    'website': 'http://www.ProoSoft.com',
    'summary': 'Tax',
    'description': """
    """,
    'depends': ['hr_payslip_struct', 'hr_child', 'hr_contract_info'],
    'data': [
        'l10n_tn_pay_category_register_data.xml',
        'resource_calendar.xml',
        'l10n_tn_pay_data.xml',
        #'hr.payroll.structure.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
