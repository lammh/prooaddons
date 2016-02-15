from openerp import models,fields


class OeMedicalPathologyCategory(models.Model):
    _name = 'oemedical.pathology.category'


    childs = fields.One2many('oemedical.pathology.category',
                              'parent_id',
                              string='Children Category', )
    name = fields.Char(size=256, string='Category Name', required=True)
    parent_id = fields.Many2one('oemedical.pathology.category',
                              string='Parent Category', select=True)

    _constraints = [
        (models.Model._check_recursion, 'Error ! You cannot create recursive \n'
        'Category.', ['parent_id'])
    ]
