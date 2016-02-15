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
    _name = 'statement.general.report'
    _description = 'Report Statement General'

    _columns = {
        'name': fields.many2one('res.partner', 'Partner'),
        'date_start': fields.date('Start date', required=True),
        'date_end': fields.date('End date', required=True),
    }

    _defaults = {
        'name': lambda obj, cr, uid, context: context.get('active_id', None),
        'date_start': lambda *a: time.strftime('%Y-%m-01'),
        'date_end': lambda *a: time.strftime('%Y-12-31'),
    }

    def launch(self, cr, uid, ids, context=None):
        """
        Launch the report, and pass each value in the form as parameters
        """
        wiz = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        data['parameters'] = {
            'partner_id': context.get('active_id'),
            'date_start': wiz.date_start,
            'date_end': wiz.date_end,
        }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'statement_general',
                'datas': data,
        }

    def launch_detail(self, cr, uid, ids, context=None):
        """
        Launch the report, and pass each value in the form as parameters
        """
        wiz = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        data['parameters'] = {
            'partner_id': context.get('active_id'),
            'date_start': wiz.date_start,
            'date_end': wiz.date_end,
        }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'statement_general_detail',
                'datas': data,
        }

statement_general_report()

