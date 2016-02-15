
from openerp import models,fields

class OeMedicalDirections(models.Model):
    _name = 'oemedical.directions'


    procedure_id = fields.Many2one('oemedical.procedure',
                                    string='Procedure',required=True)
    evaluation_id = fields.Many2one('oemedical.patient.evaluation',
                                     string='Evaluation',readonly=True )
    comments = fields.Char(size=256, string='Comments')


