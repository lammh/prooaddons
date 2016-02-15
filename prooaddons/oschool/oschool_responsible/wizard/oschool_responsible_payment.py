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
from openerp import tools, api, exceptions
import openerp
from openerp.tools.translate import _
from openerp.addons.oschool import tools
import openerp.addons.decimal_precision as dp
from lxml import etree
import logging



class oschool_payment(osv.osv_memory):
    _name = 'oschool.payment'

    def onchange_period(self, cr, uid, ids, student_id, period_ids, cash, academic_year_id, all, context):
        if academic_year_id:
            period_ids = period_ids[0][2]
            academic_year = self.pool.get('oschool.academic_year').browse(cr, uid, academic_year_id)

            parent = self.pool.get('res.partner').browse(cr, uid, context['active_id'])
            periods = []
            student_ids =[]
            if all or not student_id:
                for student in parent.child_ids:
                    student_ids.append(student.id)
            else:
                student_ids = [student_id]
            cr.execute("""select distinct pol.period_id
                    from pos_order_line pol left outer join pos_order po on po.id = pol.order_id
                    where (pol.order_id is null or po.state = 'draft') and pol.student_id in %s and parent_id = %s and academic_year_id = %s""", (tuple(student_ids), parent.id, academic_year_id))
            for id in cr.fetchall():
                periods.append(id[0])
            res = {'value': {}, 'domain': {'period_ids': [('state', '=', 'draft'), ('special', '=', False), ('id', 'in', periods)]}}
            r = []
            if all:
                student_ids = [student.id for student in self.pool.get('res.partner').browse(cr, uid, context.get('active_id')).child_ids]
            else:
                student_ids = [student_id]
            for period_id in period_ids:
                if student_ids and period_id:
                    line_ids = self.pool.get('pos.order.line').search(cr, uid, [('subscriber', '=', True), ('type', '!=', 'registration'),
                                                                                ('period_id', '=', period_id), ('student_id', 'in', student_ids), ('product_id_tmpl.cash', '=', cash),
                                                                                ('order_id', '=', False)])
                    for l in line_ids:
                        r.append(l)
            res['value']['line_ids'] = r
            amount = 0.0
            for line in self.pool.get('pos.order.line').browse(cr, uid, r):
                amount += line.price_subtotal
            res['value']['amount'] = amount
            for student in self.pool.get('res.partner').browse(cr, uid, student_ids):
                if not student.allow_first_period_payment:
                    pay_s_j = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.pay_septembre_juin_together", default=None)
                    periods = self.pool.get('account.period').browse(cr, uid, period_ids)

                    first_period = academic_year.period_ids[0]
                    for period in academic_year.period_ids:
                        if period.date_start < first_period.date_start:
                            first_period = period
                    if first_period.date_start < student.date:
                        period_obj = self.pool.get('account.period')
                        first_period = period_obj.browse(cr, uid, period_obj.search(cr, uid, [
                            ('company_id', '=', tools.get_default_company(self, cr, uid)),
                            ('date_start', '<=', student.date),
                            ('date_stop', '>=', student.date),
                        ]))
                    if pay_s_j:
                        for period in periods:
                            if period.id == first_period.id:
                                res['warning'] = {
                                                'title': "Warning!",
                                                'message': "The option pay first and last periods together is checked!",
                                                }
                                break
            return res
        return {}

    def button_payment(self, cr, uid, ids, context=None):
        pos_ref = self.pool.get('pos.order')
        pos_line_ref = self.pool.get('pos.order.line')
        journal_obj = self.pool.get('account.journal')

        pay_s_j = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.pay_septembre_juin_together", default=None, context=context)
        groups_id = self.pool.get("res.users").browse(cr, uid, uid).groups_id
        cashier_group = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool','oschool_group_cashier_scolarity')[1]

        is_cashier = False
        for group in groups_id:
            if group.id == cashier_group:
                is_cashier = True
                break
        for line in self.browse(cr, uid, ids, context=context):
            academic_year = line.academic_year_id
            student = line.student_id
            first_period = academic_year.period_ids[0]
            last_period = academic_year.period_ids[0]
            for period in academic_year.period_ids:
                if period.date_start < first_period.date_start:
                    first_period = period
                if period.date_start > last_period.date_start:
                    last_period = period

            if first_period.date_start < student.date:
                    period_obj = self.pool.get('account.period')
                    first_period = period_obj.browse(cr, uid, period_obj.search(cr, uid, [
                        ('company_id','=',tools.get_default_company(self,cr,uid)),
                        ('date_start','<=',student.date),
                        ('date_stop','>=',student.date),
                    ]))

            period_ids =[]
            last = False
            first = False
            for period in line.period_ids:
                if period.id ==  last_period.id:
                    last = True
                if period.id ==  first_period.id:
                    first = True
                period_ids.append(period.id)

            if not student.allow_first_period_payment:
                if is_cashier and pay_s_j and not last and first:
                    raise osv.except_osv(_('Warning!'), _('You are not allowed to pay only the first period! Please contact your school administartor'))

            l = pos_line_ref.search(cr, uid, [
                ('subscriber', '=', True),
                ('type', '!=', 'registration'),
                ('period_id', 'in', period_ids ),
                ('student_id', '=', line.student_id.id),
                ('product_id_tmpl.cash', '=', line.cash),
                ('order_id', '=', False)], order="period_id")
            if not l:
                raise osv.except_osv(_('Warning!'), _('No matching record found'))
            pos = ''
            period = line.period_ids[0]
            if not (len(period_ids) == 2 and pay_s_j and first and last):
                if first and last:
                    for p in line.period_ids:
                        if period.date_start < p.date_start and int(p.date_start[5:-3]) != 6:
                            period = p
                else:
                    for p in line.period_ids:
                        if period.date_start < p.date_start:
                            period = p
                cr.execute("""select distinct ap.id from pos_order_line pol inner join account_period ap on ap.id = pol.period_id
                           left outer join pos_order po on po.id = pol.order_id
                           where pol.type != 'registration' and pol.student_id = %s and ap.date_start < %s
                           and (pol.order_id is null or po.state = 'draft')""", (line.student_id.id, period.date_start))
                for id in cr.fetchall():
                    if id[0] not in period_ids:
                        pos += self.pool.get('account.period').browse(cr, uid, id, context=context).name + ' ,'
                if pos:
                    raise osv.except_osv(_('Warning!'), _('period %s is not paid') % pos)
            if pos_line_ref.browse(cr, uid, l[0], context=context).order_id:
                inv_id = pos_line_ref.browse(cr, uid, l[0], context=context).order_id.id
            else:
                inv = {
                    'partner_id': line.responsible_id.id,
                    'pricelist_id': line.responsible_id.property_product_pricelist.id,
                    'student_id': line.student_id.id}
                inv_id = pos_ref.create(cr, uid, inv, context=context)

                if line.cash:
                    journal_registration = journal_obj.search(cr, uid, [('cash', '=', True)], context.context)
                    if journal_registration:
                        cr.execute('update pos_order set sale_journal = %s where id = %s', (journal_registration[0], inv_id))
                for pos_line in l:
                    pos_line_ref.write(cr, uid, pos_line, {'order_id': inv_id}, context=context)

            amount = line.amount
            for pos_line in pos_line_ref.browse(cr, uid, l):
                amount -= pos_line.price_subtotal
                if amount > 0:
                    pos_line_ref.write(cr, uid, pos_line.id, {'order_id': inv_id}, context=context)
                else:
                    new = pos_line_ref.copy(cr, uid, pos_line.id, {'price_unit': -amount}, context=context)
                    old = pos_line_ref.write(cr, uid, pos_line.id, {'price_unit': pos_line.price_subtotal + amount, 'order_id': inv_id}, context=context)
                    break

        mod_obj = self.pool.get('ir.model.data')
        if is_cashier:
            res = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')
        else:
            res = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_registration_pos_form')
        res_id = res and res[1] or False
        return {
            'name': _('Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', inv_id)],
            'target' : 'new',
            'view_id': [res_id],
            'res_id': inv_id,
        }

    def button_payment_global(self, cr, uid, ids, context=None):
        pos_ref = self.pool.get('pos.order')
        pos_line_ref = self.pool.get('pos.order.line')
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')

        pay_s_j = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.pay_septembre_juin_together", default=None, context=context)
        groups_id = self.pool.get("res.users").browse(cr, uid, uid).groups_id
        cashier_group = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool','oschool_group_cashier_scolarity')[1]

        is_cashier = False
        for group in groups_id:
            if group.id == cashier_group:
                is_cashier = True
                break
        for line in self.browse(cr, uid, ids, context=context):
            academic_year = line.academic_year_id
            first_period = academic_year.period_ids[0]
            last_period = academic_year.period_ids[0]
            for period in academic_year.period_ids:
                if period.date_start < first_period.date_start:
                    first_period = period
                if period.date_start > last_period.date_start:
                    last_period = period

            if line.all:
                students = [student.id for student in self.pool.get('res.partner').browse(cr, uid, context.get('active_id')).child_ids]
            else:
                students = [line.student_id]

            for student in self.pool.get('res.partner').browse(cr, uid, students):
                if first_period.date_start < student.date:
                    first_period = period_obj.browse(cr, uid, period_obj.search(cr, uid, [
                        ('company_id', '=', tools.get_default_company(self, cr, uid)),
                        ('date_start', '<=', student.date),
                        ('date_stop', '>=', student.date),
                    ]))

                period_ids = []
                last = False
                first = False
                for period in line.period_ids:
                    if period.id ==  last_period.id:
                        last = True
                    if period.id ==  first_period.id:
                        first = True
                    period_ids.append(period.id)

                if not student.allow_first_period_payment:
                    if is_cashier and pay_s_j and not last and first:
                        raise osv.except_osv(_('Warning!'), _('You are not allowed to pay only the first period! Please contact your school administartor'))


                pos = ''
                period = line.period_ids[0]
                if not (len(period_ids) == 2 and pay_s_j and first and last):
                    if first and last:
                        for p in line.period_ids:
                            if period.date_start < p.date_start and int(p.date_start[5:-3]) != 6:
                                period = p
                    else:
                        for p in line.period_ids:
                            if period.date_start < p.date_start:
                                period = p
                    cr.execute("""select distinct ap.id from pos_order_line pol inner join account_period ap on ap.id = pol.period_id
                               left outer join pos_order po on po.id = pol.order_id
                               inner join product_product pp on pp.id = pol.product_id
                               inner join product_template pt on pt.id = pp.product_tmpl_id
                               where pol.type != 'registration' and pol.student_id = %s and ap.date_start < %s
                               and subscriber= True and cash = %s
                               and (pol.order_id is null or po.state = 'draft')""", (student.id, period.date_start, line.cash))
                    for id in cr.fetchall():
                        if id[0] not in period_ids:
                            pos += self.pool.get('account.period').browse(cr, uid, id, context=context).name + ' ,'
                    if pos:
                        raise osv.except_osv(_('Warning!'), _('period %s is not paid') % pos)
            inv = {
                'partner_id': line.responsible_id.id,
                'pricelist_id': line.responsible_id.property_product_pricelist.id
            }
            inv_id = pos_ref.create(cr, uid, inv, context=context)
            if line.cash:
                journal_registration = journal_obj.search(cr, uid, [('cash', '=', True)], context.context)
                if journal_registration:
                    cr.execute('update pos_order set sale_journal = %s where id = %s', (journal_registration[0], inv_id))
            l = pos_line_ref.search(cr, uid, [
                    ('subscriber', '=', True),
                    ('type', '!=', 'registration'),
                    ('period_id', 'in', period_ids),
                    ('student_id', 'in', students),
                    ('product_id_tmpl.cash', '=', line.cash),
                    ('order_id', '=', False)], order="period_id")
            if not l:
                raise osv.except_osv(_('Warning!'), _('No matching record found'))
            amount = line.amount
            for pos_line in pos_line_ref.browse(cr, uid, l):
                amount -= pos_line.price_subtotal
                if amount >= 0:
                    pos_line_ref.write(cr, uid, pos_line.id, {'order_id': inv_id}, context=context)
                    if amount == 0:
                        break
                else:
                    new = pos_line_ref.copy(cr, uid, pos_line.id, {'price_unit': -amount}, context=context)
                    old = pos_line_ref.write(cr, uid, pos_line.id, {'price_unit': pos_line.price_subtotal + amount, 'order_id': inv_id}, context=context)
                    break

        mod_obj = self.pool.get('ir.model.data')
        if is_cashier:
            res = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')
        else:
            res = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_registration_pos_form')
        res_id = res and res[1] or False
        return {
            'name': _('Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'domain': [('id', '=', inv_id)],
            'target' : 'new',
            'view_id': [res_id],
            'res_id': inv_id,
        }

    _columns = {
        'responsible_id': fields.many2one('res.partner', 'Responsible'),
        'student_id': fields.many2one('res.partner', 'Student', domain="[('parent_id','=', responsible_id), ('active_student', '=', True)]"),
        'academic_year_id': fields.many2one('oschool.academic_year', 'Academic year'),
        'period_ids': fields.many2many('account.period'),
        'line_ids': fields.many2many('pos.order.line', 'payment_line_rel', 'payment_id', 'line_id', string="Lines"),
        'cash': fields.boolean("Cash"),
        'all': fields.boolean("All"),
        'amount': fields.float(string='Amount', digits_compute=dp.get_precision('Account'), required=1),
    }

    _defaults = {
        'academic_year_id' : lambda self, cr, uid, context: self.default_academic_year(cr, uid, context),
    }

    def default_academic_year(self, cr, uid, context):
        year_obj = self.pool.get('oschool.academic_year')
        year_id = year_obj.search(cr, uid,[
                                         ('state','=', 'current'),
                                            ('company_id','=',tools.get_default_company(self,cr,uid))
                                         ])
        if year_id:
            return  year_id[0]
        else:
            return False



oschool_payment()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

