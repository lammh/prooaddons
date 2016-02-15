from openerp import models,fields,api


class MedicalPhysician(models.Model):
    _name = 'medical.doctor'
    _inherits={
        'res.partner': 'partner_id',
    }

    partner_id = fields.Many2one('res.partner', string='Doctor',required=True , domain=[('category_id', '=', 'Physician')], ondelete='cascade')
    code = fields.Char(size=256, string='ID')
    info = fields.Text(string='info')
    specialty = fields.Many2one('medical.specialty', string='Specialty', required=True, help='Specialty Code')
