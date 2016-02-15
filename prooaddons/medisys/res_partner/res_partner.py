from openerp import models,fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_patient = fields.Boolean(string='Patient',
                                 help='Check if the party is a patient')
    is_doctor = fields.Boolean(string='Doctor',
                        help='Check if the party is a doctor')
    is_pharmacy = fields.Boolean(string='Pharmacy',
                                  help='Check if the party is a Pharmacy')
    is_insurance_company = fields.Boolean(string='Insurance Company',
                        help='Check if the party is an Insurance Company')
    ref = fields.Char(size=256, string='SSN',
                       help='Patient Social Security Number or equivalent')

