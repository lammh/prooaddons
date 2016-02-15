from openerp import models,fields,api


class OeMedicalPhysician(models.Model):
    _name = 'oemedical.physician'

    # def _get_name(self, cr, uid, ids, field_name, arg, context=None):
    #     res = {}
    #     for record in self.browse(cr, uid, ids, context=context):
    #         res[record.id] = record.physician_id.name
    #     return res

    @api.one
    @api.depends('physician_id')
    def _get_name(self):
        self.name = self.physician_id.name


    physician_id = fields.Many2one('res.partner', string='Health Professional',required=True , help='Physician' ,domain=[('category_id', '=', 'Physician')]  )
    code = fields.Char(size=256, string='ID')
    name = fields.Char(compute = '_get_name', string='Health Professional', help="",store=True)
    specialty = fields.Many2one('oemedical.specialty', string='Specialty',required=True, help='Specialty Code')
    institution = fields.Many2one('res.partner', string='Institution', help='Instituion where she/he works',domain=[('is_company', '=', 'True')] )
    info = fields.Text(string='Extra info')
