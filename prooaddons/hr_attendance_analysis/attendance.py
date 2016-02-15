# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################

from openerp import tools
import openerp.addons.decimal_precision as dp
from openerp.osv import fields,osv

class account_statement(osv.osv):
    _name = "hr.attandence.analysis"
    _description = "Attendance Analysis"
    _auto = False
    _rec_name = 'employee_id'
    _order  = 'date desc, hours'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'date': fields.date('Date'),
        'action': fields.selection([('sign_in', 'Sign in'), ('sign_out', 'Sign out')], "Action Type"),
        'hours': fields.char('Hours'),
    }

    def init(self, cr):

        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW hr_attandence_analysis as (
                select id, employee_id, to_date(to_char(name, 'DD/MM/YYYY'::text), 'DD-MM-YYYY') date, action, to_char(name, 'HH24:MI:SS'::text) as hours
                from hr_attendance
                order by date desc, hours
        )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
