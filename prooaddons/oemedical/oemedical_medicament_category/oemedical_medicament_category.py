from openerp import models,fields


class OeMedicalMedicamentCategory(models.Model):
    _name = 'oemedical.medicament.category'


    childs = fields.One2many('oemedical.medicament.category',
                              'parent_id', string='Children', )
    name = fields.Char(size=256, string='Name', required=True)
    parent_id = fields.Many2one('oemedical.medicament.category',
                              string='Parent', select=True)

    _constraints = [
        (models.Model._check_recursion, 'Error ! You cannot create recursive \n'
        'Category.', ['parent_id'])
    ]