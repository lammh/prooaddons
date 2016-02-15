from openerp import models,fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    #'insurance_plan_ids': fields.one2many('oemedical.insurance.plan',
    #                                       'relation_id',
    #                                       string='Insurance Plans', ),
    is_insurance_company = fields.Boolean(string='Insurance Company',
                        help='Check if the party is an Insurance Company')
    relationship = fields.Char(size=256, string='Relationship')
    insurance_company_type = fields.Selection([
        ('state', 'State'),
        ('labour_union', 'Labour Union / Syndical'),
        ('private', 'Private'), ],
        string='Insurance Type',select=True)
    is_institution = fields.Boolean(string='Institution',
                            help='Check if the party is a Medical Center')
    relative_id = fields.Many2one('res.partner', string='Contact', )
    is_doctor = fields.Boolean(string='Health Prof',
                        help='Check if the party is a health professional')
    is_patient = fields.Boolean(string='Patient',
                                 help='Check if the party is a patient')
    alias = fields.Char(size=256, string='Alias',
                         help='Common name that the Party is reffered')
    internal_user = fields.Many2one('res.users', string='Internal User',
    help='In GNU Health is the user (doctor, nurse) that logins.When the'\
    ' party is a doctor or a health professional, it will be the user'\
    ' that maps the doctor\'s party name. It must be present.')
    activation_date = fields.Date(string='Activation date',
                                   help='Date of activation of the party')
    lastname = fields.Char(size=256, string='Last Name', help='Last Name')
    is_work = fields.Boolean(string='Work')
    is_person = fields.Boolean(string='Person',
                                help='Check if the party is a person.')
    is_school = fields.Boolean(string='School')
    is_pharmacy = fields.Boolean(string='Pharmacy',
                                  help='Check if the party is a Pharmacy')
    ref = fields.Char(size=256, string='SSN',
                       help='Patient Social Security Number or equivalent')
    #'insurance': fields.one2many('oemedical.insurance', 'relation_id',
        #                               string='Insurance', ),
