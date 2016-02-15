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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.osv import osv
from openerp.exceptions import except_orm

class account_invoice(models.Model):
    _inherit = "account.invoice"

    withholding = fields.Many2many('account.voucher', relation='invoice_voucher_rel', column1='invoice_id', column2='voucher_related',
                                domain="[('type', '=', 'withholding_payment'), ('state', '=', 'posted')]")
    residual = fields.Float(string='Balance', digits=dp.get_precision('Account'), compute='_compute_residual', store=True, help="Remaining amount due.")

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line.price_subtotal',
        'move_id.line_id.account_id.type',
        'move_id.line_id.amount_residual',
        # Fixes the fact that move_id.line_id.amount_residual, being not stored and old API, doesn't trigger recomputation
        'move_id.line_id.reconcile_id',
        'move_id.line_id.amount_residual_currency',
        'move_id.line_id.currency_id',
        'move_id.line_id.reconcile_partial_id.line_partial_ids.invoice.type',
    )
    def _compute_residual(self):
        self.residual = 0.0
        # Each partial reconciliation is considered only once for each invoice it appears into,
        # and its residual amount is divided by this number of invoices
        partial_reconciliations_done = []
        for line in self.sudo().move_id.line_id:
            if line.account_id.type not in ('receivable', 'payable') or line.partner_id != self.partner_id:
                continue
            if line.reconcile_partial_id and line.reconcile_partial_id.id in partial_reconciliations_done:
                continue
            # Get the correct line residual amount
            if line.currency_id == self.currency_id:
                line_amount = line.amount_residual_currency if line.currency_id else line.amount_residual
            else:
                from_currency = line.company_id.currency_id.with_context(date=line.date)
                line_amount = from_currency.compute(line.amount_residual, self.currency_id)
            # For partially reconciled lines, split the residual amount
            if line.reconcile_partial_id:
                partial_reconciliation_invoices = set()
                for pline in line.reconcile_partial_id.line_partial_ids:
                    if pline.invoice and self.type == pline.invoice.type:
                        partial_reconciliation_invoices.update([pline.invoice.id])
                line_amount = self.currency_id.round(line_amount / len(partial_reconciliation_invoices))
                partial_reconciliations_done.append(line.reconcile_partial_id.id)
            self.residual += line_amount
        self.residual = max(self.residual, 0.0)

    @api.one
    def importation_file(self):
        if self.state != 'open':
            raise osv.except_osv(_('Error!'), _('You cannot merge move.'))
        for invoice_related in self.invoices:
            if invoice_related.state != 'open':
                raise osv.except_osv(_('Error!'), _('You cannot merge move.'))
            for move_line in invoice_related.move_id.line_id:
                self._cr.execute("UPDATE account_move_line set move_id = %s where id = %s", (self.move_id.id, move_line.id))
            self._cr.execute("UPDATE account_invoice set move_id = %s where id = %s", (self.move_id.id, invoice_related.id))
            self._cr.execute("DELETE FROM account_move where id = %s", (invoice_related.move_id.id,))

        #for withholding in self.withholding:
        #    for move_line in withholding.move_id.line_id:
        #        self._cr.execute("UPDATE account_move_line set move_id = %s where id = %s", (self.move_id.id, move_line.id))
        #    self._cr.execute("UPDATE account_voucher set move_id = %s where id = %s", (self.move_id.id, withholding.id))
        #    self._cr.execute("DELETE FROM account_move where id = %s", (withholding.move_id.id,))
        return True

    @api.one
    def cancel_file(self):
        if not self.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))

        #for withholding in self.withholding:
        #    withholding.write({'state': 'cancel', 'move_id': False})

        moves = self.env['account.move']
        for inv in self:
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids:
                        raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid or paid. You need to unreconcile related payment entries first.'))

        for inv in self.invoices:
            if inv.payment_ids:
                for move_line in inv.payment_ids:
                    if move_line.reconcile_partial_id.line_partial_ids or move_line.reconcile_ref:
                        raise except_orm(_('Error!'), _('You cannot cancel an invoice which is partially paid or paid. You need to unreconcile related payment entries first.'))

        move_id = self.move_id
        for line in self.move_id.line_id:
            self._cr.execute("DELETE FROM account_move_line where id = %s", (line.id,))
        for invoice_related in self.invoices:
            invoice_related.write({'state': 'cancel', 'move_id': False})
        self.write({'state': 'cancel', 'move_id': False})
        self._cr.execute("DELETE FROM account_move where id = %s", (move_id.id,))
        self._log_event(-1.0, 'Cancel Invoice')
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
