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

class customer_invoice_unpaid(osv.osv_memory):
    _name = 'customer.invoice.unpaid'
    _description = 'Customer Invoice Unpaid'

    _columns = {
        'date': fields.date('Date'),
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-12-31'),
    }

    def launch(self, cr, uid, ids, context=None):
        """
        Launch the report, and pass each value in the form as parameters
        """
        wiz = self.browse(cr, uid, ids, context=context)[0]
        data = {}
        data['parameters'] = {
            'date': wiz.date,
        }

        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'customer_invoice_unpaid',
                'datas': data,
        }

customer_invoice_unpaid()

