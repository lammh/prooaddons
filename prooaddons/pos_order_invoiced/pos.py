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
from openerp.tools.translate import _
from openerp import netsvc

class account_journal(osv.osv):
    _inherit = "account.journal"

    _columns = {
        'cash': fields.boolean('Cash'),
    }

account_journal()

class account_journal(osv.osv):
    _inherit = "product.template"

    _columns = {
        'cash': fields.boolean('Cash'),
    }

account_journal()

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'pos_ids': fields.one2many('pos.order', 'invoice_id', 'Orders Pos', readonly=True),
    }

    def invoice_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'open'}, context=context)
        order_obj = self.pool.get('pos.order')
        move_line_obj = self.pool.get('account.move.line')
        period_obj = self.pool.get('account.period')
        journal_obj = self.pool.get('account.journal')
        journal = journal_obj.search(cr, uid, [('type','=','cash')], context=context)
        writeoff_acc_id = journal_obj.browse(cr, uid, journal[0], context=context).loss_account_id.id
        for invoice in self.browse(cr, uid, ids, context=context):
            data_lines = []
            nbr = len(invoice.pos_ids)
            l = 0
            for order in invoice.pos_ids:
                l += 1
                invoice = order.invoice_id
                data_lines += [x.id for x in invoice.move_id.line_id if x.account_id.id == invoice.account_id.id]
                for st in order.statement_ids:
                    writeoff_journal_id = st.journal_id.id
                    writeoff_period_id = period_obj.find(cr, uid, context=dict(context or {}, company_id=st.journal_id.company_id.id, account_period_prefer_normal=True))[0]
                    for move in st.journal_entry_id:
                        data_lines += [x.id for x in move.line_id if x.account_id.id == invoice.account_id.id]
                if nbr > l:
                    move_line_obj.reconcile_partial(cr, uid, list(set(data_lines)), writeoff_acc_id=writeoff_acc_id, writeoff_journal_id=writeoff_journal_id, writeoff_period_id=writeoff_period_id, context=context)
                else:
                    move_line_obj.reconcile(cr, uid, list(set(data_lines)), writeoff_acc_id=writeoff_acc_id, writeoff_journal_id=writeoff_journal_id, writeoff_period_id=writeoff_period_id, context=context)
        return True

class pos_session(osv.osv):
    _inherit = "pos.session"

    def wkf_action_close(self, cr, uid, ids, context=None):
        res = super(pos_session, self).wkf_action_close(cr, uid, ids, context=context)
        for session in self.browse(cr, uid, ids, context=context):
            for order in session.order_ids:
                if order.state == 'invoiced' and order.invoice_id.state == 'open':
                    invoice = order.invoice_id
                    data_lines = [x.id for x in invoice.move_id.line_id if x.account_id.id == invoice.account_id.id]
                    for st in order.statement_ids:
                        writeoff_journal_id = st.journal_id.id
                        writeoff_period_id = self.pool.get('account.period').find(cr, uid, context=dict(context or {}, company_id=st.journal_id.company_id.id, account_period_prefer_normal=True))[0]
                        writeoff_acc_id = st.journal_id.with_last_closing_balance and st.journal_id.loss_account_id.id or False
                        for move in st.journal_entry_id:
                            data_lines += [x.id for x in move.line_id if x.account_id.id == invoice.account_id.id]
                    self.pool.get('account.move.line').reconcile(cr, uid, data_lines, writeoff_acc_id=writeoff_acc_id, writeoff_journal_id=writeoff_journal_id, writeoff_period_id=writeoff_period_id, context=context)
        return res

pos_session()

class pos_order(osv.osv):
    _inherit = "pos.order"

    def create_invoices(self, cr, uid, partner_id, pos_lines, context=None):
        pos_grouped = {}
        inv_ids = []
        move_unlink = []
        statement_ids = []
        wf_service = netsvc.LocalService("workflow")
        inv_ref = self.pool.get('account.invoice')
        inv_line_ref = self.pool.get('account.invoice.line')
        product_obj = self.pool.get('product.product')
        statement_obj = self.pool.get('account.bank.statement')
        statement_line_obj = self.pool.get('account.bank.statement.line')
        move_line_obj = self.pool.get('account.move.line')
        origin = ''
        for order in pos_lines:
            inv = {
                'account_id': partner_id.property_account_receivable.id,
                'journal_id': order.sale_journal.id or None,
                'type': 'out_invoice',
                'partner_id': partner_id.id,
                'currency_id': order.pricelist_id.currency_id.id,
                }
            inv.update(inv_ref.onchange_partner_id(cr, uid, [], 'out_invoice', partner_id.id)['value'])
            key = (order.sale_journal.id, order.pricelist_id.currency_id.id)
            if not key in pos_grouped: 
                pos_grouped[key] = inv
                inv_id = inv_ref.create(cr, uid, inv, context=context)
                pos_grouped[key].update({'invoice_id': inv_id})
                for statement_line in order.statement_ids:
                    statement_line_obj.write(cr, uid, statement_line.id,{'partner_id': partner_id.id}, context=context)
                    for move in statement_line.journal_entry_id:
                        for line in move.line_id:
                            move_line_obj.write(cr, uid, line.id,{'partner_id': partner_id.id}, context=context)
                if order.account_move.id:
                    move_unlink.append(order.account_move.id)
                self.write(cr, uid, [order.id], {'partner_id': partner_id.id}, context=context)
                self.write(cr, uid, [order.id], {'invoice_id': inv_id, 'state': 'invoiced'}, context=context)
                inv_ids.append(inv_id)
            else:
                for statement_line in order.statement_ids:
                    statement_line_obj.write(cr, uid, statement_line.id,{'partner_id': partner_id.id}, context=context)
                    for move in statement_line.journal_entry_id:
                        for line in move.line_id:
                            move_line_obj.write(cr, uid, line.id,{'partner_id': partner_id.id}, context=context)
                if order.account_move.id:
                    move_unlink.append(order.account_move.id)
                self.write(cr, uid, [order.id], {'partner_id': partner_id.id}, context=context)
                self.write(cr, uid, [order.id], {'invoice_id': pos_grouped[key]['invoice_id'], 'state': 'invoiced'}, context=context)

            for line in order.lines:
                inv_line = {
                    'invoice_id': pos_grouped[key]['invoice_id'],
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }
                inv_name = product_obj.name_get(cr, uid, [line.product_id.id], context=context)[0][1]
                inv_line.update(inv_line_ref.product_id_change(cr, uid, [],
                                                               line.product_id.id,
                                                               line.product_id.uom_id.id,
                                                               line.qty, partner_id = partner_id.id,
                                                               fposition_id=partner_id.property_account_position.id)['value'])
                if line.product_id.description_sale:
                    inv_line['note'] = line.product_id.description_sale
                inv_line['price_unit'] = line.price_unit
                inv_line['discount'] = line.discount
                inv_line['name'] = inv_name
                inv_line['invoice_line_tax_id'] = [(6, 0, [x.id for x in line.product_id.taxes_id] )]
                inv_line_ref.create(cr, uid, inv_line, context=context)

        # Supprimer la Pièces comptable du journal vente
        self.pool.get('account.move').unlink(cr, uid, list(set(move_unlink)), context=context)

        for inv in inv_ids:
            inv_ref.button_reset_taxes(cr, uid, [inv], context=context)

        if not inv_ids: return {}

        action = {}
        action_model,action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', "action_invoice_tree1")
        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,inv_ids))+"])]"

        return action

pos_order()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
