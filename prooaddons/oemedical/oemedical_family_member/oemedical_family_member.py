from openerp import models,fields


class OeMedicalFamilyMember(models.Model):
    _name = 'oemedical.family_member'

    member = fields.Many2one('res.partner', string='Member',
                              help='Family Member Name')
    role = fields.Char(size=256, string='Role', required=True)
    family_id = fields.Many2one('oemedical.family', string='Family',
                                 help='Family code')
