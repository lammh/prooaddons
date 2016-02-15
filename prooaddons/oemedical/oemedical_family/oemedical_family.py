from openerp import models,fields


class OeMedicalFamily(models.Model):
    _name = 'oemedical.family'

    info = fields.Text(string='Extra Information')
    operational_sector = fields.Many2one('oemedical.operational_sector',
                                          string='Operational Sector', )
    name = fields.Char(size=256, string='Family', required=True,
                        help='Family code within an operational sector')
    members = fields.One2many('oemedical.family_member', 'family_id',
                               string='Family Members', )

    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Family Code must be unique!'),
    ]