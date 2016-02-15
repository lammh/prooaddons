from openerp import models,fields


class OeMedicalInsurancePlan(models.Model):
    _name = 'oemedical.insurance.plan'


    name = fields.Char(string='Name', size=264,required=True,
                        help='Insurance company plan')
    is_default = fields.Boolean(string='Default plan',
    help='Check if this is the default plan when assigning this insurance'\
    ' company to a patient')
    company = fields.Many2one('res.partner', string='Insurance Company',
                               required=True)
    notes = fields.Text(string='Extra info')
    plan = fields.Many2one('product.product', string='Plan')
