{
    'name': 'HR CNSS',
    'version': '1.0',
    'author': 'ProoSoft',
    'category': 'Human Resources',
    'sequence': 1,
    'website': 'http://www.ProoSoft.com',
    'summary': 'HR CNSS Statement',
    'description': """
    """,
    'depends': ['l10n_tn_pay'],
    'data': [
        'hr_statement_view.xml',
        'hr_report_menu.xml',
	'security/ir.model.access.csv',
    
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
