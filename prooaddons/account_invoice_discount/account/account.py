# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.tools.translate import _
from openerp.addons.l10n_tn_taxes.amount_to_text_fr import amount_to_text

class account_account(models.Model):
    _inherit = 'account.account'
    
    flag_discount = fields.Boolean("Discount Flag", default=False,
            help="NOTE: Use it for only one account. Is the account for discount in move line")

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'account_invoice_discount.report_invoice')

    @api.multi
    def discount_apply(self):
        if self.discount_method == "amount":
            account_invoice_tax = self.env['account.invoice.tax']
            self.global_discount = 0.0
            ctx = dict(self._context)
            for invoice in self:
                amount_tax_whitout = 0.0
                self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
                self.invalidate_cache()
                partner = invoice.partner_id
                if partner.lang:
                    ctx['lang'] = partner.lang
                    for taxe in account_invoice_tax.compute(invoice.with_context(ctx)).values():
                        account_invoice_tax.create(taxe)
                amount_tax = sum(line.amount for line in self.tax_line)
                amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
                amount_total = self.amount_untaxed + self.amount_tax
                for line in self.tax_line:
                    if line.base == 0.0:
                        amount_tax_whitout += line.amount
                if amount_total - amount_tax_whitout == 0:
                    self.global_discount = 100
                else:
                    self.global_discount = self.global_discount_amount * 100 / (amount_total - amount_tax_whitout)
        else:
            self.global_discount_amount = 0.0
            for line in self.invoice_line:
                self.global_discount_amount += (line.price_unit * line.quantity) * (self.global_discount / 100)
        self.button_reset_taxes()
        self.amount_in_word = amount_to_text(self.amount_total, lang='fr', currency='Dinars')
        return True

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount')
    def _compute_amount(self):
        self.amount_tax = sum(line.amount for line in self.tax_line)
        discount = (100.00 - self.global_discount) / 100.00
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line) * discount
        self.amount_total = self.amount_untaxed + self.amount_tax
        self.amount_in_word = amount_to_text(self.amount_total, lang='fr', currency='Dinars')

    discount_method = fields.Selection([('percentage', 'Percentage'), ('amount',    'Amount')], string="Discount Method", default='percentage')
    global_discount = fields.Float("Global Discount", states={'draft': [('readonly',False)]}, default= 0, digits=(16,8), help="Invoice Global Discount [0-100]")
    global_discount_amount = fields.Float("Global Discount", states={'draft': [('readonly',False)]}, default= 0, digits=dp.get_precision('Product Price'), store=True)

    amount_untaxed = fields.Float(string='Subtotal', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_tax = fields.Float(string='Tax', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount')

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        account_discount_id = self.env['account.account'].search([('flag_discount', '=', True)])
        if not account_discount_id:
            raise Warning(_('Warning !'), _('There must be, an account whit flag_discount=True, to compute move lines!'))
        total_amount = 0.0
        for m in move_lines:
            if m[2]['credit'] > 0.0:
                total_amount += m[2]['credit']

        new_line = {'analytic_account_id': False, 'tax_code_id': False, 'analytic_lines': [],
            'tax_amount': False, 'name': _('Global Discount'), 'ref': '',
            'analytics_id': False, 'currency_id': False, 'debit': False ,
            'product_id': False, 'date_maturity': False, 'credit': False, 'date': move_lines[0][2]['date'],
            'amount_currency': 0, 'product_uom_id': False, 'quantity': 1, 'partner_id': move_lines[0][2]['partner_id'],
            'account_id': account_discount_id.id}

        if self.global_discount > 0.00:
            num_lines=0
            for m in move_lines:
                if self.type in ('out_refund', 'in_invoice'):
                    if m[2]['credit'] > 0.0:
                        num_lines += 1
                else:
                    if m[2]['debit'] > 0.0:
                        num_lines += 1
            discount_amount = (total_amount - self.amount_total) / num_lines
            for m in move_lines:
                if self.type in ('out_refund', 'in_invoice'):
                    if m[2]['credit'] > 0.0:
                        m[2]['credit'] -= discount_amount
                else:
                    if m[2]['debit'] > 0.0:
                        m[2]['debit'] -= discount_amount

        precision = self.env['decimal.precision'].precision_get('Account')
        debit=credit=0.0
        for m in move_lines:
            m[2]['debit'] = round(m[2]['debit'], precision)
            m[2]['credit'] = round(m[2]['credit'], precision)
            debit += m[2]['debit']
            credit += m[2]['credit']
        precision_diff = round(credit - debit, precision)
        if precision_diff != 0.0:
            if precision_diff < 0.0:
                new_line['credit'] = abs(precision_diff)
            else:
                new_line['debit'] = precision_diff
            move_lines += [(0,0,new_line)]
        return move_lines

account_invoice()

class account_invoice_tax(models.Model):
    _inherit = "account.invoice.tax"

    @api.v8
    def compute(self, invoice):
        tax_grouped = super(account_invoice_tax, self).compute(invoice)
        discount = (100.00 - invoice.global_discount) / 100.00

        for t in tax_grouped.values():
            if t['base'] != 0:
                t['base'] *= discount
                t['amount'] *= discount
                t['base_amount'] *= discount
                t['tax_amount'] *= discount
        return tax_grouped

account_invoice_tax()
