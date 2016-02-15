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
import logging



class oschool_payment(osv.osv_memory):
    _name = 'oschool.period.payment'

    def onchange_period(self, cr, uid, ids, student_id, period_ids,academic_year_id):
        if academic_year_id:
            period_ids = period_ids[0][2]
            academic_year = self.pool.get('oschool.academic_year').browse(cr, uid, academic_year_id)
            periods = []

            for period in academic_year.period_ids:
                periods.append(period.id)
            res = {'value': {}, 'domain':{'period_ids':[('id','in',periods)]}}
            r = []
            for period_id in period_ids:
                if student_id and period_id:
                    line_ids = self.pool.get('pos.order.line').search(cr, uid,
                                                                      [
                                                                        ('period_id', '=', period_id),
                                                                       ('student_id', '=', student_id),
                                                                       ('order_id', '=', False)])
                    for l in line_ids:
                        r.append(l)
            res['value']['line_ids'] = r
            return res
        return {}




    _columns = {
        'responsible_id': fields.many2one('res.partner', 'Responsible'),
        'student_id': fields.many2one('res.partner', 'Student', domain="[('parent_id','=', responsible_id), ('active_student', '=', True)]"),
        'academic_year_id': fields.many2one('oschool.academic_year', 'Academic year'),
        'period_ids': fields.many2many('account.period', domain="[('state', '=', 'draft')]"),
        'line_ids': fields.many2many('pos.order.line', 'payment_line_rel', 'payment_id', 'line_id', string="Lines"),
        'cash': fields.boolean("Cash")
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
    _defaults = {
                 'academic_year_id' : lambda self, cr, uid, context: self.default_academic_year(cr, uid, context)
                }


oschool_payment()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

