{
    'name': 'Salary Grid',
    'version': '1.0.0',
    'category': 'Human Resources',
    'sequence': 3,
    'author': 'ProoSoft',
    'summary': 'Salary Grid',
    'description': 'Make Salary Grid for each employee',
    'depends': ["hr_payslip_struct", "hr_contract_info"],
    'data': ['hr_salary_grid_view.xml','security/ir.model.access.csv'],
      
    'installable': True,
    'application': False,
    'auto_install': False,
}
