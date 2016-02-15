# -*- coding: utf-8 -*-
from openerp import models, fields, _
from openerp.osv import osv

class account_voucher(models.Model):
    _inherit = 'account.voucher'

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)
        if res and partner_id:
            if ttype == 'receipt':
                res['value']['holder'] = self.pool.get('res.partner').browse(cr, uid, partner_id).name
            else:
                res['value']['holder'] = self.pool.get('account.journal').browse(cr, uid, journal_id).company_id.name
        return res

    def cancel_voucher(self, cr, uid, ids, context=None):
        super(account_voucher, self).cancel_voucher(cr, uid, ids, context)
        for treasury in self.browse(cr, uid, ids).treasury_ids:
            if treasury.state not in ('draft', 'valid', 'cancel'):
                raise osv.except_osv(_('Warning!'), _('You cannot delete Treasury Document number %s !') % (treasury.name,))
            self.pool.get('account.treasury').unlink(cr, uid, treasury.id)
        return True

    def proforma_voucher(self, cr, uid, ids, context=None):
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.journal_id.type == 'bank' and voucher.type_document.generate:
                res = {
                    'name': voucher.id_document,
                    'amount': voucher.amount,
                    'partner_id': voucher.partner_id.id,
                    'holder': voucher.holder,
                    'type_transaction': voucher.type,
                    'type': voucher.type_document.id,
                    'bank_source': voucher.bank_source.id,
                    'clearing_date': voucher.clearing_date,
                    'reception_date': voucher.date,
                    'state': 'valid',
                    'voucher_ids':[(6, 0, [x.id for x in voucher])]
                }
                self.pool.get('account.treasury').create(cr, uid, res, context=context)
        self.action_move_line_create(cr, uid, ids, context=context)
        voucher_line_obj = self.pool.get('account.voucher.line')
        for credit in self.browse(cr, uid, ids, context=context).line_cr_ids:
            if credit.amount == 0:
                credit.unlink()
        for debit in self.browse(cr, uid, ids, context=context).line_dr_ids:
            if debit.amount == 0:
                debit.unlink()
        return True

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

    treasury_ids = fields.Many2many('account.treasury', 'account_voucher_treasury_rel', 'voucher_id', 'treasury_id', 'Associated Treasuries', readonly=True)
    type_journal = fields.Selection(related='journal_id.type')
    id_document = fields.Char('Document ID',size=64, select=1, readonly=True, states={'draft':[('readonly', False)]})
    holder = fields.Char('Holder', size=128, readonly=True,states={'draft':[('readonly',False)]},
                                     help="Holder who made the pay with this document.")
    type_document = fields.Many2one('account.treasury.type', 'Document Type', select=1, readonly=True, states={'draft':[('readonly', False)]})
    bank_source = fields.Many2one('res.bank','Source Bank', readonly=True, states={'draft':[('readonly', False)]})
    clearing_date = fields.Date('Clearing Date', readonly=True, states={'draft':[('readonly', False)]})

    
class account_move_line(models.Model):
    _inherit = 'account.move.line'

    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if name:
            ids = self.search(cr, user, [('ref',operator,name)]+ args, limit=limit, context=context)
        else:
            ids = self.search(cr, user, args, limit=limit, context=context)
        result = self.name_get(cr, user, ids, context=context)
        return result


