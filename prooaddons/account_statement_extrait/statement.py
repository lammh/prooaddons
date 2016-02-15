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

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        currency_obj = self.pool.get('res.currency')
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            debit = credit = 0.0
            sign = voucher.type == 'payment' and -1 or 1
            for l in voucher.line_dr_ids:
                debit += l.amount
            for l in voucher.line_cr_ids:
                credit += l.amount
            currency = voucher.currency_id or voucher.company_id.currency_id
            res[voucher.id] =  currency_obj.round(cr, uid, currency, voucher.amount - sign * (credit - debit))
        return res

    _columns = {
        'writeoff_amount': fields.function(_get_writeoff_amount, string='Difference Amount', type='float', readonly=True, store=True, digits_compute=dp.get_precision('Account'),
                                           help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
    }

account_voucher()

class account_statement(osv.osv):
    _name = "account.statement.report"
    _description = "Customer Statement"
    _auto = False
    _rec_name = 'partner_id'
    _order  = 'id desc'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'ID Partner'),
        'partner': fields.char('Partner'),
        'date': fields.date('Date'),
        'description': fields.char('Description'),
        'number': fields.char('Number'),
        'price_unit': fields.float('Price', digits=dp.get_precision('Product Price')),
        'debit': fields.float('Debit', digits=dp.get_precision('Account')),
        'credit': fields.float('Credit', digits=dp.get_precision('Account')),
        'solde': fields.float('Solde', digits=dp.get_precision('Account')),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_statement')
        cr.execute("""CREATE or REPLACE VIEW account_statement as (
                select ROW_NUMBER() over (order by date, create_date) as id, *
                from (select rp.id partner_id, rp.name as partner, ai.date_invoice as date, case when ai.type = 'out_invoice' then 'VENTE ' when ai.type = 'out_refund' then 'AVOIR ' end || round(ail.quantity, 0) || 'X ' || ail.name as description,
                number, case when ai.type = 'out_invoice' then round(ail.price_unit * quantity, 3) * (1 - (ail.discount / 100)) else 0 end debit,
                case when ai.type = 'out_refund' then round(ail.price_unit * quantity, 3) * (1 - (ail.discount / 100)) else 0 end credit, ail.price_unit * (1 - (ail.discount / 100)) as price_unit, ail.create_date
                from account_invoice_line ail inner join account_invoice ai on ai.id = ail.invoice_id
                inner join res_partner rp on rp.id = ai.partner_id
                where ai.state not in ('draft','cancel')
                union all
                select rp.id partner_id, rp.name as partner, ai.date_invoice as date, 'TIMBRE FISCAL' as description,
                number, case when ai.type = 'out_invoice' then round(aii.tax_amount, 3) else 0 end debit,case when ai.type = 'out_refund' then round(aii.tax_amount, 3) else 0 end credit, 0, ai.create_date
                from account_invoice_tax aii inner join account_invoice ai on ai.id = aii.invoice_id inner join res_partner rp on rp.id = ai.partner_id
                where ai.state not in ('draft','cancel') and aii.base = 0
                union all
                select rp.id partner_id, rp.name as partner, ai.date_invoice as date, 'REMISE' as description,
                number, case when ai.type = 'out_refund' then round(ai.global_discount_amount, 3) else 0 end debit,case when ai.type = 'out_invoice' then round(ai.global_discount_amount, 3) else 0 end credit, 0, ai.create_date
                from account_invoice ai inner join res_partner rp on rp.id = ai.partner_id
                where ai.state != 'cancel' and ai.global_discount_amount > 0
                union all
                select rp.id partner_id, rp.name, av.date, 'ESPECE ' || coalesce(av.reference, ''), number, 0, amount, 0, av.create_date
                from account_voucher av inner join account_journal aj on aj.id = av.journal_id
                inner join res_partner rp on rp.id = av.partner_id
                where aj.type = 'cash' and state='posted'
                union all
                select rp.id partner_id, rp.name, av.date, att.name || ' ' || coalesce(av.reference, ''), number, 0, amount, 0, av.create_date
                from account_voucher av inner join account_journal aj on aj.id = av.journal_id
                inner join res_partner rp on rp.id = av.partner_id inner join account_treasury_type att on att.id = av.type_document
                where aj.type = 'bank' and state='posted' and att.generate = False
                union all
                select rp.id partner_id, rp.name, av.date, aj.name || ' ' || coalesce(av.reference, ''), number, 0, amount, 0, av.create_date
                from account_voucher av inner join account_journal aj on aj.id = av.journal_id
                inner join res_partner rp on rp.id = av.partner_id
                where aj.type = 'withholding_sale' and state='posted'
                union all
                select av.partner_id, holder, av.date, aa.name , av.number, 0, -av.writeoff_amount, 0, av.create_date
                from account_voucher av inner join account_account aa on aa.id = av.writeoff_acc_id
                where av.state ='posted' and av.payment_option = 'with_writeoff'
                union all
                select at.partner_id, holder, reception_date, att.name || ' ' || case when bank_source is not null then rb.name end || ' N° ' || at.name || ' Du ' || clearing_date, at.name, 0, amount, 0, at.create_date
                from account_treasury at inner join res_bank rb on rb.id = at.bank_source inner join account_treasury_type att on att.id = at.type
                where at.state not in ('rejected', 'cancel', 'warranty') ) as statement order by partner_id, date, number
        )""")
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW account_statement_report as (
                select *, (SELECT sum(debit) - sum(credit) FROM account_statement WHERE partner_id = asr.partner_id and id <= asr.id) as solde
                from account_statement asr order by id desc
        )""")

class account_statement_general(osv.osv):
    _name = "account.statement.report.general"
    _description = "Customer Statement"
    _auto = False
    _rec_name = 'partner_id'
    _order  = 'id desc'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'ID Partner'),
        'partner': fields.char('Partner'),
        'date': fields.date('Date'),
        'description': fields.char('Description'),
        'number': fields.char('Number'),
        'debit': fields.float('Debit', digits=dp.get_precision('Account')),
        'credit': fields.float('Credit', digits=dp.get_precision('Account')),
        'solde': fields.float('Solde', digits=dp.get_precision('Account')),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_statement_general')
        cr.execute("""CREATE or REPLACE VIEW account_statement_general as (
                select ROW_NUMBER() over (order by date, create_date) as id, *
                from (select rp.id partner_id, rp.name as partner, ai.date_invoice as date, case when ai.type = 'out_invoice' then 'VENTE' when ai.type = 'out_refund' then 'AVOIR' end as description,
                number, case when ai.type = 'out_invoice' then ai.amount_total else 0 end debit,
                case when ai.type = 'out_refund' then amount_total else 0 end credit, ai.create_date
                from account_invoice ai inner join res_partner rp on rp.id = ai.partner_id
                where ai.state not in ('draft','cancel')
                union all
                select rp.id partner_id, rp.name, av.date, 'ESPECE ' || coalesce(av.reference, ''), number, 0, amount, av.create_date
                from account_voucher av inner join account_journal aj on aj.id = av.journal_id
                inner join res_partner rp on rp.id = av.partner_id
                where aj.type = 'cash' and state='posted'
                union all
                select rp.id partner_id, rp.name, av.date, att.name || ' ' || coalesce(av.reference, ''), number, 0, amount, av.create_date
                from account_voucher av inner join account_journal aj on aj.id = av.journal_id
                inner join res_partner rp on rp.id = av.partner_id inner join account_treasury_type att on att.id = av.type_document
                where aj.type = 'bank' and state='posted' and att.generate = False
                union all
                select rp.id partner_id, rp.name, av.date, aj.name || ' ' || coalesce(av.reference, ''), number, 0, amount, av.create_date
                from account_voucher av inner join account_journal aj on aj.id = av.journal_id
                inner join res_partner rp on rp.id = av.partner_id
                where aj.type = 'withholding_sale' and state='posted'
                union all
                select av.partner_id, holder, av.date, aa.name , av.number, 0, -av.writeoff_amount, av.create_date
                from account_voucher av inner join account_account aa on aa.id = av.writeoff_acc_id
                where av.state ='posted' and av.payment_option = 'with_writeoff'
                union all
                select at.partner_id, holder, reception_date, att.name || ' ' || case when bank_source is not null then rb.name end || ' N° ' || at.name || ' Du ' || clearing_date, at.name, 0, amount, at.create_date
                from account_treasury at inner join res_bank rb on rb.id = at.bank_source  inner join account_treasury_type att on att.id = at.type
                where at.state not in ('rejected', 'cancel','warranty') ) as statement order by partner_id, date, number
        )""")
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW account_statement_report_general as (
                select *, (SELECT sum(debit) - sum(credit) FROM account_statement_general WHERE partner_id = asr.partner_id and id <= asr.id) as solde
                from account_statement_general asr order by id desc
        )""")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
