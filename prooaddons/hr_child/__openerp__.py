{
    'name': 'Child Employee',
    'version': '1.0.0',
    'category': 'Human Resources',
    'sequence': 3,
    'author': 'ProoSoft',
    'summary': 'Manange employee',
    'description': 'Add child to emlpoyee',
    'depends': ["hr_payroll"],
    'data': ['hr_child_view.xml', 'hr_child_data.xml','security/ir.model.access.csv'],
      
    'installable': True,
    'application': False,
    'auto_install': False,
}
