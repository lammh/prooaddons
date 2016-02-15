{
    'name': 'Contract Info',
    'version': '1.0.0',
    'category': 'Human Resources',
    'sequence': 3,
    'author': 'ProoSoft',
    'summary': 'Add info (CNSS,FOPRLOLOS,TFP,etc)',
    'description': 'Add info to contact of employee',
    'depends': ["hr_contract"],
    'data': ['hr_contract_info_view.xml','hr_contract_data.xml','security/ir.model.access.csv'],
      
    'installable': True,
    'application': False,
    'auto_install': False,
}
