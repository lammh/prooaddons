{

    'name': 'Medisys : Clinic Information System',
    'version': '1.0',
    'author': "ERP SYSTEMS",
    'category': 'Generic Modules/Others',
    'depends': ['base', 'sale', 'purchase', 'account_accountant', 'product'],
    'application': True,
    'description': """

About Medisys
---------------

Medisys is a multi-user, highly scalable, centralized Electronic
Medical Record (EMR) and Clinic Information System for Odoo.
    
""",
    "website": "http://e-erp-sys.com",
    "licence": "AGPL v3",
    "data": [
        'sequence/medical_sequence.xml',
        'medical_menu.xml',
        'res_partner/res_partner_view.xml',
        'product/product_view.xml',
        'invoice/invoice_view.xml',
        'medical_room/medical_room_view.xml',
        'medical_specialty/medical_specialty_data.xml',
        'medical_specialty/medical_specialty_view.xml',
        'medical_doctor/medical_doctor_view.xml',
        'medical_patient/patient_cron_room.xml',
        'medical_patient/medical_patient_view.xml',
#        'security/ir.model.access.csv',
        'views/theme.xml'
    ],
    "active": False
}
