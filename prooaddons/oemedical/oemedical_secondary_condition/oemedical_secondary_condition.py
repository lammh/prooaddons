from openerp import models,fields


class OeMedicalSecondaryCondition(models.Model):
    _name = 'oemedical.secondary_condition'

    pathology_id = fields.Many2one('oemedical.pathology',
                                        string='Pathology', required=True)
    evaluation_id = fields.Many2one('oemedical.patient.evaluation',
                                         string='Evaluation', readonly=True)
    comments = fields.Char(size=256, string='Comments')

