from openerp import models,fields


class OeMedicalHospitalBuilding(models.Model):
    _name = 'oemedical.hospital.building'

    code = fields.Char(size=8, string='Code')
    institution = fields.Many2one('res.partner', string='Institution',
                                   help='Medical Center')
    name = fields.Char(size=256, string='Name', required=True,
                        help='Name of the building within the institution')
    extra_info = fields.Text(string='Extra Info')
