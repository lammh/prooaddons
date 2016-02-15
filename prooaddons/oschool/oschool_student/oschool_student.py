# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#/#############################################################################
from openerp.osv import osv, fields
from openerp import models, api, SUPERUSER_ID
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from lxml import etree
import time

class school_history(osv.osv):
    _name = 'oschool.history'
    _order = 'date_start desc'

    _columns = {
        'name': fields.many2one('oschool.academic_year', 'Academic Year'),
        'date_start': fields.related('name', 'date_start', type='date', string='Start Date', store=True),
        'student_id': fields.many2one('res.partner', 'Student'),
        'group_id': fields.many2one('oschool.groups', 'Group'),
        'class_id': fields.many2one('oschool.classes', 'Class'),
        'average': fields.float('Average', digits_compute=dp.get_precision('Discount')),
    }

school_history()

class oschool_relationship(osv.osv):
    _name = "res.partner.relationship"

    _columns = {
        'name': fields.char('Name', required="1", translate=True),
    }

oschool_relationship()

class oschool_student(osv.osv):
    _inherit = 'res.partner'

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        if context is None: context = {}
        if view_type == 'form':
            if self.pool.get('res.partner').browse(cr, uid, context.get('active_id')).is_responsible:
                result = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_responsible_form')
                result = result and result[1] or False
                view_id = result
            if self.pool.get('res.partner').browse(cr, uid, context.get('active_id')).is_student:
                result = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_student_form')
                result = result and result[1] or False
                view_id = result

        res = super(oschool_student, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res

    def create(self, cr, uid, vals, context=None):

        if vals.has_key('is_responsible'):
            current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            vals['company_id'] = current_user.company_id.parent_id.id

        new_id = super(oschool_student, self).create(cr, uid, vals, context=context)
        if self.browse(cr, uid, new_id, context=context).is_student:
            self.write(cr, uid, [new_id], {'ref': self.pool.get('ir.sequence').get(cr, uid, 'partner.student') or '/'}, context=context)
        return new_id

    def unlink(self, cr, uid, ids, context=None):
        for partner_id in ids:
            lines = False
            type = ''
            partner = self.browse(cr, uid, partner_id, context=context)
            if partner.is_student:
                type = _('student')
                lines = self.pool.get('pos.order.line').search(cr, uid, [('student_id', '=', partner_id)], context=context)
            if partner.is_responsible:
                type = _('responsible')
                lines = partner.child_ids
            if len(lines) > 0:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a %s') % (type,))
        return super(oschool_student, self).unlink(cr, uid, ids, context=context)

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        if context is None:
            context = {}
        if not use_parent_address:
            return {'value':{'street': False, 'city': False, 'state_id': False, 'zip': False, 'country_id': False}}
        if 'default_parent_id' in context:
            parent_id = context.get('default_parent_id')
        res = super(oschool_student, self).onchange_address(cr, uid, ids, use_parent_address, parent_id, context=context)
        if 'default_is_student' in context and context.get('default_is_student', False):
            if 'value' not in res:
                res = {'value': {}}
            res['value']['property_product_pricelist'] = self.browse(cr, uid, parent_id, context=context).property_product_pricelist.id
        return res


    def onchange_birthdate(self, cr, uid, ids, birthdate, admission_date, context=None):
        if context is None:
            context = {}
        res = {'value': {}}
        if not birthdate or not admission_date:
            return res

        if birthdate >= admission_date:
            return {'value': {'birthdate': False}, 'warning': {'title': _('Warning!'), 'message': _('Birthdate must be before admission date.')}}
        return res

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                if record.parent_id.ref:
                    name = "[%s] %s %s, %s %s" % (record.parent_id.ref, record.parent_name, record.parent_id.last_name, name, record.last_name)
                else:
                    name = "%s %s, %s %s" % (record.parent_name, record.parent_id.last_name, name, record.last_name)
            if record.is_responsible:
                name = "[%s] %s %s" % (record.ref, name, record.last_name)
            if context.get('show_address_only'):
                name = self._display_address(cr, uid, record, without_company=True, context=context)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            res.append((record.id, name))
        return res

    _columns = {
        'is_student': fields.boolean('Is Student'),
        'active_student': fields.boolean('Active'),
        'birthdate': fields.date('Birthdate'),
        'birthplace': fields.char('Birthplace'),
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender'),
        'relationship_id': fields.many2one('res.partner.relationship', 'Relationship'),
        'academic_year_id': fields.many2one('oschool.academic_year', 'Academic Year'),
        'group_id': fields.many2one('oschool.groups', 'Group'),
        'class_id': fields.many2one('oschool.classes', 'Class'),
        'average': fields.float('Average', digits_compute=dp.get_precision('Discount')),
        'history_ids': fields.one2many('oschool.history', 'student_id', 'History'),
        'allow_registration': fields.boolean(string='Allow registration', default=1),
        'allow_first_period_payment': fields.boolean(string='Allow payment for the first period only', default=0,
                                                     help="A student who has this option checked can pay only the first period, if the option pay the first and last period together is checked."),
    }

    _defaults = {
        'date': fields.datetime.now,
    }
oschool_student()

class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'

    _columns = {
        'order_id': fields.many2one('pos.order', 'Order Ref', ondelete='set null'),
        'state_order': fields.related('order_id', 'state', type='selection', selection=[('draft', 'New'), ('cancel', 'Cancelled'), ('paid', 'Paid'), ('done', 'Posted'), ('invoiced', 'Invoiced')], string='Order State'),
        'student_id': fields.many2one('res.partner', 'Student', ondelete='restrict'),
        'parent_id': fields.related('student_id', 'parent_id', type='many2one', relation='res.partner', string='Responsible', store=True),
        'period_id': fields.many2one('account.period', 'Period'),
        'date_start': fields.related('period_id', 'date_start', type='date', string='Start of Period'),
        'class_id': fields.many2one('oschool.classes', 'Class'),
        'group_id': fields.many2one('oschool.groups', 'Group'),
        'academic_year_id': fields.many2one('oschool.academic_year', 'Academic year'),
        'state_academic_year': fields.related('academic_year_id', 'state', type='char', string='State Academic year'),
        'type': fields.char('Type', size=64),
        'refunded': fields.boolean('Refunded'),
    }

    def create(self, cr, uid, values, context=None):
        res = super(pos_order_line, self).create(cr, uid, values, context=context)
        period_obj = self.pool.get('account.period')
        if not 'academic_year_id' in values or 'academic_year_id' in values and not values['academic_year_id']:
            values['acedemic_year_id'] = self.pool.get('product.product').browse(cr, uid, values['product_id']).pos_categ_id.academic_year.id
        if 'type' in values:
            if values['type'] == 'extra':
                create_date = time.strftime('%Y-%m-%d')
                period_id = period_obj.search(cr, uid, [('date_start', '<=', create_date), ('date_stop', '>=', create_date), ('state', '=', 'draft')], context=context)
                if not period_id:
                    raise osv.except_osv(_('Warning!'), _('There is no period defined for this date: %s.') % create_date)
                self.write(cr, uid, res, {'period_id': period_id[0], 'academic_year_id': values['academic_year_id']}, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.type == 'registration':
                if rec.order_id and rec.order_id.state != 'draft':
                    raise osv.except_osv(_('Unable to Delete!'), _('Can not delete the order line %s' % (rec.product_id.name,)))
                else:
                    self.pool.get('res.partner').write(cr, uid, rec.student_id.id, {'group_id': False, 'class_id': False})
            elif (rec.order_id and rec.qty > 0) or (rec.order_id and rec.order_id.state != 'draft'):
                raise osv.except_osv(_('Unable to Delete!'), _('Can not delete the order line %s' % (rec.product_id.name,)))
        return super(pos_order_line, self).unlink(cr, uid, ids, context=context)

pos_order_line()

class pos_order(osv.osv):
    _inherit = 'pos.order'

    def _get_pos_from_lines(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('pos.order.line')
        return [line.order_id.id for line in line_obj.browse(cr, uid, ids, context=context)]

    def _get_journal(self, cr, uid, ids, fieldnames, args, context=None):
        result = dict.fromkeys(ids, False)
        journal_obj = self.pool.get('account.journal')
        for pos_order in self.browse(cr, uid, ids, context=context):
            journal_id = pos_order.session_id.config_id.journal_id.id
            for line in pos_order.lines:
                if line.type == 'registration':
                    if not journal_obj.search(cr, uid, [('registration', '=', True),('company_id','=',pos_order.company_id.id)], limit=1, context=context):
                        raise osv.except_osv(_('Error!'), _('No registration journal type'))
                    journal_id = journal_obj.search(cr, uid, [('registration', '=', True),('company_id','=',pos_order.company_id.id)], limit=1, context=context)[0]
                elif line.type == 'club' or line.type == 'extra':
                    journal_id = journal_obj.search(cr, uid, [('extra', '=', True),('company_id','=',pos_order.company_id.id)], limit=1, context=context)[0]
                elif line.product_id.cash and pos_order.partner_id.cash:
                    journal_id = journal_obj.search(cr, uid, [('cash', '=', True)], limit=1, context=context)[0]
            result[pos_order.id] = journal_id
        return result

    _columns = {
        'sale_journal': fields.function(_get_journal, type="many2one", string="Sale Journal", relation="account.journal", store=True),
        'student_id': fields.related('lines', 'student_id', type="many2one", relation="res.partner", string="Student", store={
            _inherit: (lambda self, cr, uid, ids, c: ids, ['lines'], 10),
            'pos.order.line': (_get_pos_from_lines, ['student_id'], 10)
            }),
    }
pos_order()

class academic_year(models.Model):
    _inherit = 'oschool.academic_year'

    def action_current(self, cr, uid, ids, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        current = self.search(cr, uid, [('state', '=', 'current'),('company_id','=',current_user.company_id.id)])
        if len(current) > 0:
            raise ValidationError(_("School year with the current state already exist"))

        for line_id in self.pool.get('pos.order.line').search(cr, uid, [
            ('type', '=', 'registration'),
            ('academic_year_id', '=', ids),
            ('qty', '!=', -1),
            ('refunded', '=', False)]):
            line = self.pool.get('pos.order.line').browse(cr, uid, line_id, context=context)
            self.pool.get('res.partner').write(cr, uid, line.student_id.id, {'academic_year_id': line.academic_year_id.id, 'class_id': line.class_id.id, 'group_id': line.group_id.id})
        return self.write(cr, uid, ids, {'state': 'current'})

    def action_closed(self, cr, uid, ids, context=None):
        for line_id in self.pool.get('pos.order.line').search(cr, uid, [('academic_year_id', '=', ids), ('qty', '!=', -1)]):
            line = self.pool.get('pos.order.line').browse(cr, uid, line_id, context=context)
            if line.order_id:
                if line.order_id.state == "draft":
                    raise osv.except_osv(_('Error!'), _('You cannot close this academic year, because %s have not ''paid'' status.' % (line.order_id.name)))
        #on chercher l'année scolaire avec l'état new
        #sachant qu'il n'y aura q'une seule instance
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        new_year = self.search(cr, uid, [('state','=','new'),
                                             ('company_id','=',current_user.company_id.parent_id.id)
                                             ])

        for line_id in self.pool.get('pos.order.line').search(cr, uid, [
                                                            ('type', '=', 'registration'),
                                                            ('academic_year_id', '=', ids),
                                                            ('qty', '!=', -1),
                                                            ('refunded', '=', False)]):
            line = self.pool.get('pos.order.line').browse(cr, uid, line_id, context=context)
            res = {
                'name': line.academic_year_id.id,
                'student_id': line.student_id.id,
                'group_id': line.group_id.id,
                'class_id': line.student_id.class_id.id,
            }
            #pour ajouter la classe à l'inscription
            #Ceci pour le cas de l'ouverture de l'année scolaire àprés sa ferméture.
            self.pool.get('pos.order.line').write(cr, uid, line_id, {'class_id':line.student_id.class_id.id}, context=context)
            self.pool.get('oschool.history').create(cr, uid, res)

            #si une instance avec etat new exist
            if new_year:
                #on cherche une inscription pour cet élève dans cette année
                new_reg = self.pool.get('pos.order.line').search(cr, uid, [('type', '=', 'registration'),
                                                                            ('academic_year_id', '=', new_year),
                                                                            ('qty', '!=', -1),
                                                                            ('refunded', '=', False),
                                                                           ('student_id', '=', line.student_id.id),
                                                                           ])
                #s'il existe une inscription dans la nouvelle année on met à jour le profil élève
                if new_reg:
                    reg = self.pool.get('pos.order.line').browse(cr, uid, new_reg.id)
                    self.pool.get('res.partner').write(cr, uid, line.student_id.id, {
                        'academic_year_id': new_year.id,
                        'group_id': reg.group_id.id,
                        'class_id': reg.class_id.id})
                #si non on met false
                else:
                    self.pool.get('res.partner').write(cr, uid, line.student_id.id, {'academic_year_id': False, 'group_id': False, 'class_id': False})
            else:
                self.pool.get('res.partner').write(cr, uid, line.student_id.id, {'academic_year_id': False, 'group_id': False, 'class_id': False})
        return self.write(cr, uid, ids, {'state': 'closed'})

academic_year()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
