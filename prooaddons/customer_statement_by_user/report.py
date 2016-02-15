# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Domsense s.r.l. (<http://www.domsense.com>).
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

from openerp.osv import osv, fields
import time

class statement_general_report(osv.osv_memory):
    _name = 'statement.general.report.user'
    _description = 'Report Statement By User'

    _columns = {
        'name': fields.many2one('res.users', 'User', required=True),
    }

    def launch(self, cr, uid, ids, context=None):
        """
        Launch the report, and pass each value in the form as parameters
        """
        wiz = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        data['parameters'] = {
            'user_id': wiz.name.id,
        }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'statement_by_user',
                'datas': data,
        }

statement_general_report()

