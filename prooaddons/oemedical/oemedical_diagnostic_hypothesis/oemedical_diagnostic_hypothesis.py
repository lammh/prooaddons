
from openerp import models,fields


class OeMedicalDiagnosticHypothesis(models.Model):
    _name = 'oemedical.diagnostic_hypothesis'


    pathology_id = fields.Many2one('oemedical.pathology', 'Pathology',
                                    required=True )
    evaluation_id = fields.Many2one('oemedical.patient.evaluation',
                                     'Evaluation',readonly=True )
    comments = fields.Char(size=256, string='Comments')