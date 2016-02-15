# -*- coding: utf-8 -*-

#################################################################################
#    Autor: Mikel Martin (mikel@zhenit.com)
#    Copyright (C) 2012 ZhenIT Software (<http://ZhenIT.com>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class res_partner(osv.osv):
    _inherit = "res.partner"

    def _invoice_total(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        invoice_obj = self.pool.get('account.invoice')
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        user_currency_id = user.company_id.currency_id.id
        for partner_id in ids:
            amount = 0.0
            invoice_ids = invoice_obj.search(cr, uid, [('partner_id', '=', partner_id), ('state', 'not in', ['draft', 'cancel'])])
            for invoice in invoice_obj.browse(cr, uid, invoice_ids):
                if invoice.type == 'out_invoice':
                    amount += invoice.amount_total
                elif invoice.type == 'out_refund':
                    amount -= invoice.amount_total
            result[partner_id] = amount

        return result

    _columns = {
        'total_invoiced': fields.function(_invoice_total, string="Total Invoiced", type='float', groups='account.group_account_invoice', digits=dp.get_precision('Account')),
    }

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
