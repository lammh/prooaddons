{
    'name': 'Loan Emloyee',
    'version': '1.0',
    'author': 'ProoSoft',
    'category': 'Human Resources',
    'sequence': 1,
    'website': 'http://www.ProoSoft.com',
    'summary': 'Loan Employees Details',
    'description': """
    """,
    'depends': ['hr_payslip_struct'],
    'data': [
        'security/ir.model.access.csv',
        'hr_loan_view.xml',
        'loan_sequence.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
