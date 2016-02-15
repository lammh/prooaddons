from openerp import models,fields


class OeMedicalInsurance(models.Model):
    _name = 'oemedical.insurance'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.company.name
        return res



    name = fields.Char(compute ='_get_name', string='Name', help="", multi=False)
    company = fields.Many2one('res.partner', 'Insurance Company', required=True)
    patient_id = fields.Many2one('oemedical.patient', 'Patient')
    plan_id = fields.Many2one('oemedical.insurance.plan', string='Plan',  help='Insurance company plan')
    insurance_type = fields.Selection([
        ('state', 'State'),
        ('labour_union', 'Labour Union / Syndical'),
        ('private', 'Private'),
    ], string='Insurance Type',select=True)
    number = fields.Char(size=256, string='Number', required=True)
    member_since = fields.Date(string='Member since')
    member_exp = fields.Date(string='Expiration date')
    notes = fields.Text(string='Extra Info')
    owner = fields.Many2one('res.partner', string='Owner')

