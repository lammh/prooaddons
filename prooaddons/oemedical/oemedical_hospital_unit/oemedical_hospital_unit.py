from openerp import models,fields


class OeMedicalHospitalUnit(models.Model):
    _name = 'oemedical.hospital.unit'

    code = fields.Char(size=8, string='Code')
    institution = fields.Many2one('res.partner', string='Institution',
                                   help='Medical Center')
    name = fields.Char(size=256, string='Name', required=True,
                help='Name of the unit, eg Neonatal, Intensive Care, ...')
    extra_info = fields.Text(string='Extra Info')
