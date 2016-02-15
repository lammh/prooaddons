{
	'name': 'HR Premium',
	'version': '1.0.0',
	'category': 'Human Resources',
	'sequence': 3,
	'author': 'ProoSoft',
	'summary': 'HR Premium',
	'description': 'Premium Management',
	'depends': ['hr_payslip_struct'],
	'data': ['hr_premium_view.xml',"security/ir.model.access.csv"],
	  
	'installable': True,
	'application': False,
	'auto_install': False,
}
