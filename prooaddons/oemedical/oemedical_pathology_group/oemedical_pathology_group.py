from openerp import models,fields


class OeMedicalPathologyGroup(models.Model):
    _name = 'oemedical.pathology.group'

    info = fields.Text(string='Detailed information')
    code = fields.Char(size=256, string='Code', required=True,
      help='for example MDG6 code will contain the Millennium Development'\
                ' Goals # 6 diseases : Tuberculosis, Malaria and HIV/AIDS')
    name = fields.Char(size=256, string='Name', required=True,
                        translate=True, help='Group name')
    desc = fields.Char(size=256, string='Short Description',
                        required=True)
