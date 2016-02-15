{
	'name': 'HR Pay',
	'version': '1.0.0',
	'category': 'Human Resources',
	'sequence': 3,
	'author': 'ProoSoft',
	'summary': 'HR Pay',
	'description': 'Pay Management',
	'depends': ['hr_payslip_struct'],
	'data': ['hr_pay_stub_view.xml','security/ir.model.access.csv'],
	  
	'installable': True,
	'application': False,
	'auto_install': False,
}
