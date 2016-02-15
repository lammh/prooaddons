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

from openerp.osv import osv, fields

class pos_invoiced(osv.osv_memory):
    _name = 'pos.invoiced'
    _description = 'Invoiced Pos Order'

    _columns = {
        'partner_id': fields.many2one('res.partner','Customer', domain="[('customer','=',True)]"),
        'order_ids': fields.many2many('pos.order', 'order_invoiced_rel', 'invoice_id', 'pos_id', 'Orders')
    }

    def invoiced_pos(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids, context=context)[0]
        return self.pool.get('pos.order').create_invoices(cr, uid, data.partner_id, data.order_ids, context)
        

pos_invoiced()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
