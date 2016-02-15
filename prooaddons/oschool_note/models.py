# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class oschool_trimester(models.Model):
    _name = 'oschool.trimester'

    name = fields.Char('Name', required=1)

class oschool_matiere_type(models.Model):
    _name = 'oschool.matiere.type'
    _order = 'sequence'

    name = fields.Char('Name', required=1)
    sequence = fields.Integer('Sequence', required=1, default=1)

class oschool_matiere(models.Model):
    _name = 'oschool.matiere'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    type = fields.Many2one('oschool.matiere.type', string='Type', required=1)
    sequence = fields.Integer('Sequence', required=1, default=1)

class oschool_matiere_group(models.Model):
    _name = 'oschool.matiere.group'
    _order = 'sequence'

    @api.one
    @api.depends('name')
    def _compute_display_name(self):
        self.name = self.group_id.name + ' ( ' + self.matiere_id.name + ' ) '

    name = fields.Char(compute='_compute_display_name', string='Name', required=1)
    sequence = fields.Integer('Sequence', required=1, default=1)
    group_id = fields.Many2one('oschool.groups', 'Group', required=1)
    matiere_id = fields.Many2one('oschool.matiere', 'Matiere', required=1)
    details_ids = fields.One2many('oschool.matiere.group.details', 'name', string='Details')

    def _default_details_ids(self, cr, uid, context=None):
        res = self.pool.get('oschool.trimester').search(cr, uid, [], context=context)
        default = {
            'value': [],
        }
        for line in res:
            rs = {
                'trimester_id':line,
                'coefficient': 1,
                'mandatory': True,
            }
            default['value'].append(rs)
        return default and default['value'] or False

    _defaults = {
        'details_ids': _default_details_ids,
        }

    _sql_constraints = [('group_matiere_unique', 'UNIQUE(group_id,matiere_id)', "Matiere/Group must be unique")]

class oschool_matiere_group(models.Model):
    _name = 'oschool.matiere.group.details'

    name = fields.Many2one('oschool.matiere.group', 'Matiere Group', ondelete='cascade')
    trimester_id = fields.Many2one('oschool.trimester', 'Trimester')
    coefficient = fields.Float('Coefficient', digits=(16, 1))
    mandatory = fields.Boolean('Mandatory')

class student_notes(models.Model):
    _name = 'student.notes'

    name = fields.Many2one('res.partner', 'Student')
    trimester_id = fields.Many2one('oschool.trimester', 'Trimester')
    academic_year = fields.Many2one('oschool.academic_year', 'Academic Year', required=1)
    average = fields.Float(string='Average', digits=(16, 2))

class oschool_note(models.Model):
    _name = 'oschool.note'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.model
    def create(self, vals):
        ctx = dict(self._context or {}, mail_create_nolog=True)
        new_id = super(oschool_note, self).create(vals, context=ctx)
        new_id.message_post(body=_("Note created"), context=ctx)
        return new_id

    @api.multi
    def onchange_note(self, academic_year, class_id, matiere_id):
        default = {'value': {'details_ids': []}}
        if class_id:
            group_id = self.env['oschool.classes'].browse(class_id).group.id
            default['value']['group_id'] = group_id
        if class_id and matiere_id:
            if self.env['oschool.classes'].browse(class_id).group.id != self.env['oschool.matiere.group'].browse(matiere_id).group_id.id:
                default['value']['matiere_id'] = False
                return default
        if not academic_year or not class_id or not matiere_id:
            return default

        students = self.env['res.partner'].search([('is_student', '=', True), ('academic_year_id', '=', academic_year), ('class_id', '=', class_id)])

        matieres = self.env['oschool.matiere.group'].browse(matiere_id)
        for student in students:
            for matiere in matieres:
                rs = {
                    'student_id':student,
                    'matiere_group': matiere,
                }
                default['value']['details_ids'].append(rs)
        return default

    @api.one
    @api.depends('name')
    def _compute_display_name(self):
        self.name = self.class_id.name + ' ( ' + self.academic_year.name + ': ' + self.trimester_id.name + ' ) '

    @api.multi
    def compute_average(self):
        student_notes_obj = self.env['student.notes']
        note_details_obj = self.env['oschool.note.details']
        matiere_group_details_obj = self.env['oschool.matiere.group.details']
        for line in self.details_ids:
            average = coefficient_total = note_total = 0.0
            for note in note_details_obj.search([('student_id', '=', line.student_id.id), ('academic_year', '=', line.academic_year.id), ('trimester_id', '=', line.trimester_id.id)]):
                if not note.absent:
                    coefficient = matiere_group_details_obj.search([('name', '=', line.matiere_group.id), ('trimester_id', '=', line.trimester_id.id)]).coefficient
                    note_total += note.note * coefficient
                    coefficient_total += coefficient
            average = round(note_total / coefficient_total, 2)
            average_student = student_notes_obj.search([('name', '=', line.student_id.id), ('trimester_id', '=', line.trimester_id.id), ('academic_year', '=', line.academic_year.id)], limit=1)
            if average_student:
                average_student.write({'average': average})
            else:
                student_notes_obj.create({'name': line.student_id.id,
                                          'trimester_id': line.trimester_id.id,
                                          'academic_year': line.academic_year.id,
                                          'average': average,
                                          })
        return True

    @api.multi
    def _compute_note(self):
        self.note_min = len(self.details_ids) > 0 and 100 or 0.0
        self.note_max = 0.0
        sum_note = 0.0
        for student in self.details_ids:
            if not student.absent:
                sum_note += student.note
                if student.note >= self.note_max:
                    self.note_max = student.note
                if student.note <= self.note_min:
                    self.note_min = student.note
        self.average = sum_note / len(self.details_ids)
        self.compute_average()
        return True

    name = fields.Char(compute='_compute_display_name', string='Name', required=1)
    academic_year = fields.Many2one('oschool.academic_year', 'Academic Year', required=1)
    group_id = fields.Many2one('oschool.groups', 'Group', required=1)
    class_id = fields.Many2one('oschool.classes', 'Class', required=1)
    trimester_id = fields.Many2one('oschool.trimester', 'Trimester', required=1)
    matiere_id = fields.Many2one('oschool.matiere.group', 'Matiere', required=1)
    note_min = fields.Float(compute='_compute_note', string='Min Note', digits=(16, 2), readonly=1)
    note_max = fields.Float(compute='_compute_note', string='Max Note', digits=(16, 2), readonly=1)
    average = fields.Float(compute='_compute_note', string='Average', digits=(16, 2), readonly=1)
    details_ids = fields.One2many('oschool.note.details', 'name', string='Details')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], 'State', readonly=True, select=1, default='draft', track_visibility='onchange')

    _sql_constraints = [('note_unique', 'UNIQUE(academic_year,group_id,trimester_id,matiere_id)', "Note must be unique")]

class oschool_note_details(models.Model):
    _name = 'oschool.note.details'

    name = fields.Many2one('oschool.note', 'Note', ondelete='cascade')
    student_id = fields.Many2one('res.partner', 'Student', domain="[('is_student', '=', True)]", required=1)
    matiere_group = fields.Many2one('oschool.matiere.group', 'Matiere Group', required=1)
    note = fields.Float('Note', digits=(16, 2))
    absent = fields.Boolean('Absent')
    matiere_id = fields.Many2one(related='name.matiere_id.matiere_id', relation='oschool.matiere', string='Matiere')
    academic_year = fields.Many2one(related='name.academic_year', relation='oschool.academic_year', string='Academic year')
    trimester_id = fields.Many2one(related='name.trimester_id', relation='oschool.trimester', string='Trimester')

class student(models.Model):
    _inherit = 'res.partner'

    notes_ids = fields.One2many('student.notes', 'name', 'Notes', readonly=1)