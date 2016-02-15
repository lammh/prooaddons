##############################################################################
#
#   Module to support witholding tax for OpenERP
#   Copyright (C) 2009, Almacom (Thailand) Ltd.
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv,fields
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class AccountWithholdingConfig(osv.TransientModel):
    _inherit = 'account.config.settings'

    _columns = {
        'withholding_auto': fields.boolean('Automatic Calculation Withholding'),
    }
AccountWithholdingConfig()

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    _columns={
        'withholding': fields.boolean('Withholding'),
             }
    _defaults = {
        'withholding': False,
    }
account_move_line()

class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
        'wht_payable_id':fields.many2one('account.tax', 'Payable Withholding', domain="[('is_wht', '=', True)]"),
        'wht_receivable_id':fields.many2one('account.tax', 'Receivable Withholding', domain="[('is_wht', '=', True)]"),
    }
res_partner()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def _get_journal(self, cr, uid, context=None):
        if context is None: context = {}
        invoice_pool = self.pool.get('account.invoice')
        journal_pool = self.pool.get('account.journal')
        if context.get('invoice_id', False):
            invoice = invoice_pool.browse(cr, uid, context['invoice_id'], context=context)
            journal_id = journal_pool.search(cr, uid, [
                ('currency', '=', invoice.currency_id.id), ('company_id', '=', invoice.company_id.id)
            ], limit=1, context=context)
            return journal_id and journal_id[0] or False
        if context.get('journal_id', False):
            return context.get('journal_id')
        if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
            return context.get('search_default_journal_id')

        ttype = context.get('type', 'bank')
        if ttype in ('payment', 'receipt'):
            ttype = 'bank'
        if ttype == 'withholding_payment':
            ttype = 'withholding_purchase'
        if ttype == 'withholding_receipt':
            ttype = 'withholding_sale'
        res = self._make_journal_search(cr, uid, ttype, context=context)
        return res and res[0] or False

    _defaults = {
        'journal_id': _get_journal,
    }

    def proforma_voucher(self, cr, uid, ids, context=None):
        voucher_line_obj = self.pool.get('account.voucher.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            for line in voucher.line_cr_ids:
                amount += line.amount
            for line in voucher.line_dr_ids:
                amount -= line.amount
            if amount == voucher.amount or amount == -voucher.amount:
                self.action_move_line_create(cr, uid, ids, context=context)
            else:
                raise osv.except_osv(_('Error!'), _('Sum line different to amount.'))

        for credit in self.browse(cr, uid, ids, context=context).line_cr_ids:
            if credit.amount == 0:
                credit.unlink()
        for debit in self.browse(cr, uid, ids, context=context).line_dr_ids:
            if debit.amount == 0:
                debit.unlink()
        return True

    def cancel_voucher(self, cr, uid, ids, context=None):
        move_line_pool = self.pool.get('account.move.line')
        super(account_voucher, self).cancel_voucher(cr, uid, ids, context)
        for voucher in self.browse(cr, uid, ids, context=context):
            for voucher_line in voucher.line_dr_ids:
                if voucher_line.amount > 0:
                    move_line_pool.write(cr, uid, voucher_line.move_line_id.id, {'withholding':False})
            for voucher_line in voucher.line_cr_ids:
                if voucher_line.amount > 0:
                    move_line_pool.write(cr, uid, voucher_line.move_line_id.id, {'withholding':False})
        return True

    def onchange_amount2(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, withholding, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        res = self.recompute_voucher_lines2(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, withholding, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        for key in vals.keys():
            res[key].update(vals[key])
        return res

    def recompute_voucher_lines2(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, withholding, context=None):
        def _remove_noise_in_o2m():
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id or not withholding:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id
        withholding = self.pool.get('account.tax').browse(cr, uid, withholding, context=context)

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'withholding_payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'

        if not context.get('move_line_ids', False):
            if account_type == 'receivable':
                ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id), ('withholding','=', False)], context=context)
            else:
                ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id), ('withholding','=', False)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_residual_withholding =  abs(withholding.amount * amount_original)
                for tax_line in line.invoice.tax_line:
                    if tax_line.base == 0 and not tax_line.manual:
                        amount_residual_withholding =  abs(withholding.amount * (amount_original-tax_line.amount))
                if amount_residual_withholding == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit and amount_residual_withholding or 0.0
                total_debit += line.debit and amount_residual_withholding or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

#        if price == 0:
#            total_credit = total_credit * withholding.amount
#            total_debit = total_debit * withholding.amount

        remaining_amount = price
        amount_to_payed = 0.0
        settings_obj = self.pool.get('account.config.settings')
        config_ids = settings_obj.search(cr, uid, [], limit=1, order='id DESC', context=context)
        account_settings = False
        if config_ids:
            account_settings = settings_obj.browse(cr, uid, config_ids[0], context=context)
        #voucher line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
                amount_withholding =  abs(withholding.amount * amount_original)
                for tax_line in line.invoice.tax_line:
                    if tax_line.base == 0 and not tax_line.manual:
                        amount_withholding =  abs(withholding.amount * amount_original-tax_line.amount)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
                amount_withholding =  currency_pool.compute(cr, uid, company_currency, currency_id, abs(withholding.amount * amount_original), context=context_multi_currency)
                for tax_line in line.invoice.tax_line:
                    if tax_line.base == 0 and not tax_line.manual:
                        amount_withholding = currency_pool.compute(cr, uid, company_currency, currency_id, abs(withholding.amount * (amount_original-tax_line.amount)), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_withholding) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'amount_withholding': amount_withholding,
                'currency_id': line_currency_id,
            }
            amount_to_payed += line.credit and amount_withholding or -amount_withholding
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_withholding, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_withholding, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['amount'] = price
            if account_settings and account_settings.withholding_auto:
                if ttype == 'withholding_payment':
                    default['value']['amount'] = amount_to_payed
                else:
                    default['value']['amount'] = -amount_to_payed
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        default['value']['type'] = ttype
        default['value']['partner_id'] = partner_id
        default['value']['date'] = date
        default['value']['journal_id'] = journal_id
        default['value']['company_id'] = journal.company_id.id
        default['value']['withholding'] = withholding.id
        return default

    def _make_journal_search(self, cr, uid, ttype, context=None):
        if ttype in ('withholding_payment', 'withholding_receipt'):
            ttype = 'withholding'
        journal_pool = self.pool.get('account.journal')
        return journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1)

    _columns={
        'withholding':fields.many2one('account.tax', 'Withholding'),
        'type': fields.selection([('sale','Sale'),
                                  ('purchase','Purchase'),
                                  ('payment','Payment'),
                                  ('receipt','Receipt'),
                                  ('withholding_payment','Withholding Payment'),
                                  ('withholding_receipt','Withholding Receipt')], string='Default Type',readonly=True, states={'draft':[('readonly',False)]}),
    }

    def onchange_withholding(self, cr, uid, ids, withholding_id, line_cr_ids, line_dr_ids, ttype, context=None):
        default = {'value': {'line_cr_ids': [] ,'line_dr_ids': [],}}
        if withholding_id:
            part = self.pool.get('account.tax').browse(cr, uid, withholding_id, context=context)
            if line_cr_ids:
                for line in line_cr_ids:
                    if line[2] != False:
                        amount_original = line[2]['amount_original']
                        line[2].update({'amount_withholding': amount_original * part.amount})
                    default['value']['line_cr_ids'].append(line)
            if line_dr_ids:
                for line in line_dr_ids:
                    if line[2] != False:
                        amount_original = line[2]['amount_original']
                        line[2].update({'amount_withholding': amount_original * part.amount})
                    default['value']['line_dr_ids'].append(line)
        return default

    def onchange_partner_id2(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, withholding, context=None):
        if not journal_id or not partner_id:
            return {}
        if context is None:
            context = {}
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if not withholding and partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if ttype == 'withholding_payment':
               res['value']['withholding'] = partner.wht_payable_id and partner.wht_payable_id.id or False
            elif partner.wht_receivable_id:
               res['value']['withholding'] = partner.wht_receivable_id and partner.wht_receivable_id.id or False

        ctx = context.copy()
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines2(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, withholding, context=ctx)
        vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])

        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        return res

    def onchange_journal2(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, withholding, context=None):
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
        vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        vals['value'].update({'currency_id': currency_id})
        res = self.onchange_partner_id2(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, withholding, context)
        for key in res.keys():
            vals[key].update(res[key])
        return vals

    def first_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        if voucher_brw.type in ('withholding_receipt', 'withholding_payment'):
            account_id = voucher_brw.withholding.account_collected_id.id
        else:
            account_id = voucher_brw.account_id.id
        if voucher_brw.type in ('purchase', 'payment'):
            credit = voucher_brw.paid_amount_in_company_currency
        elif voucher_brw.type in ('sale', 'receipt'):
            debit = voucher_brw.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        move_line = {
                'name': voucher_brw.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': account_id,
                'move_id': move_id,
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                'date': voucher_brw.date,
                'date_maturity': voucher_brw.date_due
            }
        return move_line

    def withholding_move_line_get(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        voucher_brw = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = withholding_debit = withholding_credit = 0.0
        if voucher_brw.type == 'withholding_payment':
            credit = voucher_brw.paid_amount_in_company_currency
        elif voucher_brw.type == 'withholding_receipt':
            debit = voucher_brw.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        if credit == 0:
            debit = debit - voucher_brw.amount
            withholding_debit = voucher_brw.amount
        elif debit == 0:
            credit = credit - voucher_brw.amount
            withholding_credit = voucher_brw.amount
        sign = debit - credit < 0 and -1 or 1
        withholding_line = {
                'name': voucher_brw.name or '/',
                'debit': withholding_debit,
                'credit': withholding_credit,
                'account_id': voucher_brw.withholding.account_collected_id.id,
                'move_id': move_id,
                'journal_id': voucher_brw.journal_id.id,
                'period_id': voucher_brw.period_id.id,
                'partner_id': voucher_brw.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher_brw.amount or 0.0,
                'date': voucher_brw.date,
                'date_maturity': voucher_brw.date_due
            }
        withholding_line = self.pool.get('account.move.line').create(cr, uid, withholding_line, context=context)
        return [withholding_line]

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            line_total = 0.0
            if voucher.type in ('withholding_receipt','withholding_payment'):
                move_line_id = self.withholding_move_line_get(cr, uid, voucher.id, move_id, company_currency, current_currency, context)
                move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
                for move_line in move_line_brw:
                    line_total += move_line.debit - move_line.credit
            else:
                move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
                move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
                line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
            if voucher.type in ('withholding_receipt','withholding_payment'):
                for rec in rec_list_ids:
                    move_line_pool.write(cr, uid, rec, {'withholding': True})

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True
account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id and line.voucher_id.currency_id.id or company_currency
            move_line = line.move_line_id or False
            withholding_rate = line.voucher_id.withholding.amount or 0.0
            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0
                res['amount_withholding'] = 0.0
            elif move_line.currency_id and voucher_currency==move_line.currency_id.id:
                res['amount_original'] = currency_pool.compute(cr, uid, move_line.currency_id.id, voucher_currency, abs(move_line.amount_currency), context=ctx)
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, move_line.currency_id and move_line.currency_id.id or company_currency, voucher_currency, abs(move_line.amount_residual_currency), context=ctx)
                res['amount_withholding'] = currency_pool.compute(cr, uid, move_line.currency_id and move_line.currency_id.id or company_currency, voucher_currency, abs(move_line.amount_residual_currency * withholding_rate), context=ctx)
            elif move_line and move_line.credit > 0:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit, context=ctx)
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)
                res['amount_withholding'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual * withholding_rate), context=ctx)
            else:
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.debit, context=ctx)
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)
                res['amount_withholding'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual) * withholding_rate, context=ctx)

            rs_data[line.id] = res
        return rs_data

    _columns={
        'withholding':fields.boolean('Withholding'),
        'amount_withholding': fields.function(_compute_balance, type='float', multi= 'dc', string='Withholding Amount', store=True, digits_compute=dp.get_precision('Account')),
             }
account_voucher_line()


