from openerp import models,fields


class OeMedicalProcedure(models.Model):
    _name = 'oemedical.procedure'

    description = fields.Char(size=256, string='Long Text',
                               translate=True)
    name = fields.Char(size=256, string='Code', required=True)