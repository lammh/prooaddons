##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2014 Luis Falcon, Moldeo Interactive.
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
#    test de git
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.osv import osv
from datetime import datetime
from amount_to_text_fr import amount_to_text

class account_vesement(models.Model):

    _name = "account.vesement"
    _description = 'Vesement'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.one
    def _compute_amount(self):
        self.amount = sum(line.amount for line in self.treasury_ids)

    def button_draft(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'draft'}, context=context)

    @api.one
    def account_move_get(self, vesement_id):
        seq_obj = self.pool.get('ir.sequence')
        period_obj = self.env['account.period']
        vesement = self.env['account.vesement'].browse(vesement_id)
        if vesement.journal_id.sequence_id:
            if not vesement.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))

            period = period_obj.find(dt=self.date_vesement, context=self._context)[0]
            c = dict(self._context)
            c.update({'fiscalyear_id': period.fiscalyear_id.id, 'period_id': period.id})
            name = seq_obj.next_by_id(self._cr, self._uid, vesement.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))

        ctx = self._context.copy()
        ctx.update({'company_id': vesement.company_id.id})
        period_ids = period_obj.find(dt=self._context.get('date', False), context=ctx)
        period_id = period_ids and period_ids[0] or False

        move = {
            'name': name,
            'journal_id': vesement.journal_id.id,
            'date': vesement.date_vesement,
            'ref': name,
            'period_id': period_id.id,
        }
        return move

    @api.one
    def first_move_line_get(self, vesement_id, move_id):
        vesement = self.env['account.vesement'].browse(vesement_id)
        for line in vesement.treasury_ids:
            move_line = {
                'name': line.name or '/',
                'debit': line.amount,
                'credit': 0,
                'account_id': vesement.journal_id.default_debit_account_id.id,
                'partner_id': line.partner_id.id,
                'move_id': move_id.id,
                'journal_id': vesement.journal_id.id,
                'period_id': move_id.period_id.id,
                'date': vesement.date_vesement,
                'date_maturity': vesement.date_vesement
            }
            line = self.env['account.move.line'].create(move_line)
        return move_line

    @api.one
    def vesement_move_line_create(self, vesement_id, move_id):
        rec_lst_ids = []
        vesement = self.env['account.vesement'].browse(vesement_id)
        for line in vesement.treasury_ids:
            move_line = {
                'name': line.name or '/',
                'debit': 0,
                'credit': line.amount,
                'account_id': line.voucher_ids[0].journal_id.default_credit_account_id.id,
                'partner_id': line.partner_id.id,
                'move_id': move_id.id,
                'journal_id': vesement.journal_id.id,
                'period_id': move_id.period_id.id,
                'date': vesement.date_vesement,
                'date_maturity': vesement.date_vesement
            }
            line = self.env['account.move.line'].create(move_line)
        return True

    @api.one
    def action_move_line_create(self):
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for vesement in self:
            if vesement.move_id:
                continue
            # Create the account move record.
            move_id = move_pool.create(self.account_move_get(vesement.id)[0])
            vesement.move_id = move_id
            # Create the first line of the vesement
            rec_list_ids = []
            self.first_move_line_get(vesement.id, move_id)
            self.vesement_move_line_create(vesement.id, move_id)
        return True

    @api.multi
    def button_validate(self):
        if len(self.treasury_ids) == 0:
            raise osv.except_osv(_('Error!'), _('no treasury line !'))
        treasury_obj = self.env['account.treasury']
        for treasury in self.treasury_ids:
            if treasury.state not in ('draft', 'valid'):
                raise osv.except_osv(_('Error!'), _('Document number %s for %s is not draft or validate !') % (treasury.name, treasury.partner_id.name))
            treasury.state = 'clearing'
            treasury.bank_target = self.bank_target.id
        self.amount_in_word = amount_to_text(self.amount, lang='fr', currency='Dinars')
        self.state = 'valid'
        self.action_move_line_create()
        return True

    def button_cancel(self, cr, user, ids, context=None):
        treasury_obj = self.pool.get('account.treasury')
        move_pool = self.pool.get('account.move')
        vesement = self.browse(cr, user, ids[0])
        for treasury in vesement.treasury_ids:
            if treasury.state != 'clearing':
                raise osv.except_osv(_('Error!'), _('Document number %s for %s is not clearing !') % (treasury.name, treasury.partner_id.name))
            treasury_obj.write(cr, user, treasury.id, {'state': 'valid', 'bank_target': False}, context=context)
        move_pool.button_cancel(cr, user, [vesement.move_id.id])
        move_pool.unlink(cr, user, [vesement.move_id.id])
        return self.write(cr, user, ids, {'state': 'cancel'}, context=context)

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'account.vesement', context=context) or '/'
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(account_vesement, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("Vesement created"), context=ctx)
        return new_id

    def unlink(self,cr, uid, ids, context=None):
        for vesement in self.browse(cr, uid, ids, context=context):
            if vesement.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You cannot delete this vesement !'))
        return super(account_vesement, self).unlink(cr, uid, ids, context=context)

    def onchange_date(self, cr, uid, ids, date_from, date_to, context=None):
        if context is None:
            context = {}
        if not date_from or not date_to:
            return {}
        inv = self.pool.get('account.treasury').search(cr, uid, [('state', 'in', ['draft', 'valid']),
                                                                 ('clearing_date', '>=', date_from), ('clearing_date', '<=', date_to),('type_transaction', '=', 'receipt')])
        return {'value': {'treasury_ids': [(6, 0, [x for x in inv])]}}

    def onchange_bank(self, cr, uid, ids, bank_target, context=None):
        if context is None:
            context = {}
        if not bank_target:
            return {}
        bank = self.pool.get('res.partner.bank').browse(cr, uid, bank_target)
        return {'value': {'journal_id': bank.journal_id.id}}

    name = fields.Char('Reference', copy=False, readonly=True, select=True)
    date_vesement = fields.Date(string='Vesement Date',
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    date_from = fields.Date(string='Start Date',
        readonly=True, states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='End Date',
        readonly=True, states={'draft': [('readonly', False)]})
    bank_target = fields.Many2one('res.partner.bank', 'Target Bank', readonly=True, states={'draft':[('readonly',False)]}, domain=[('company_id', '<>', False)])
    journal_id = fields.Many2one('account.journal', 'Journal', readonly=True, states={'draft':[('readonly',False)]}, domain=[('type', '=', 'bank')])
    treasury_ids = fields.Many2many('account.treasury', 'account_vesement_treasury_rel', 'vesement_id', 'treasury_id', 'Associated Document', domain="[('type_transaction', '=', 'receipt')]",
                                    readonly=True, states={'draft': [('readonly', False)]})
    amount = fields.Float(string='Total', digits=dp.get_precision('Account'), readonly=True, compute='_compute_amount')
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_id', relation='account.move.line', string='Journal Items', readonly=True)
    note = fields.Text('Notes')
    state = fields.Selection([
                                ('draft', 'Open'),
                                ('valid', 'Validate'),
                                ('cancel', 'Cancel'),
                                ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')

    _defaults = {
        'date_vesement': lambda *a: time.strftime('%Y-%m-%d'),
        'date_from': lambda *a: time.strftime('%Y-%m-%d'),
        'date_to': lambda *a: time.strftime('%Y-%m-%d'),
        }

class account_vesement_cash(models.Model):
    _name = "account.vesement.cash"
    _description = 'Cash Vesement'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Reference', copy=False, readonly=True, select=True)
    date_vesement = fields.Date(string='Vesement Date', default = lambda *a: time.strftime('%Y-%m-%d'),
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    journal_target = fields.Many2one('account.journal', 'Journal Target', readonly=True, states={'draft':[('readonly',False)]}, domain=[('type', '=', 'bank')])
    bank_target = fields.Many2one('res.partner.bank', 'Target Bank', readonly=True, states={'draft':[('readonly', False)]}, domain=[('company_id', '<>', False)])
    journal_source = fields.Many2one('account.journal', 'Journal Source', readonly=True, states={'draft':[('readonly',False)]}, domain=[('type', '=', 'cash')])
    amount = fields.Float(string='Total', digits=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]})
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, readonly=True, states={'draft':[('readonly',False)]})
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_id', relation='account.move.line', string='Journal Items', readonly=True)
    note = fields.Text('Notes')
    state = fields.Selection([
                                ('draft', 'Open'),
                                ('valid', 'Validate'),
                                ('cancel', 'Cancel'),
                                ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')

    def onchange_bank(self, cr, uid, ids, bank_target, context=None):
        if context is None:
            context = {}
        if not bank_target:
            return {}
        bank = self.pool.get('res.partner.bank').browse(cr, uid, bank_target)
        return {'value': {'journal_target': bank.journal_id.id}}

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'account.vesement.cash', context=context) or '/'
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(account_vesement_cash, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("Vesement created"), context=ctx)
        return new_id

    @api.multi
    def unlink(self):
        for vesement in self:
            if vesement.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You cannot delete this cash vesement !'))
        return super(account_vesement_cash, self).unlink()

    def button_draft(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'draft'}, context=context)

    @api.one
    def account_move_get(self, vesement_id):
        seq_obj = self.pool.get('ir.sequence')
        period_obj = self.env['account.period']
        vesement = self.browse(vesement_id)
        if vesement.journal_target.sequence_id:
            if not vesement.journal_target.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            period = period_obj.find(dt=self.date_vesement, context=self._context)[0]
            c = dict(self._context)
            c.update({'fiscalyear_id': period.fiscalyear_id.id, 'period_id': period.id})
            name = seq_obj.next_by_id(self._cr, self._uid, vesement.journal_target.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))

        ctx = self._context.copy()
        ctx.update({'company_id': vesement.company_id.id})
        period_ids = period_obj.find(dt=self._context.get('date', False), context=ctx)
        period_id = period_ids and period_ids[0] or False

        move = {
            'name': name,
            'journal_id': vesement.journal_target.id,
            'date': vesement.date_vesement,
            'ref': name,
            'period_id': period_id.id,
        }
        return move

    @api.one
    def first_move_line_get(self, vesement_id, move_id):
        vesement = self.browse(vesement_id)
        move_line = {
            'name': vesement.name or '/',
            'debit': 0,
            'credit': vesement.amount,
            'account_id': vesement.journal_source.default_debit_account_id.id,
            'move_id': move_id.id,
            'journal_id': vesement.journal_target.id,
            'period_id': move_id.period_id.id,
            'date': vesement.date_vesement,
            'date_maturity': vesement.date_vesement
        }
        line = self.env['account.move.line'].create(move_line)
        return move_line

    @api.one
    def vesement_move_line_create(self, vesement_id, move_id):
        rec_lst_ids = []
        vesement = self.browse(vesement_id)
        move_line = {
            'name': vesement.name or '/',
            'debit': vesement.amount,
            'credit': 0,
            'account_id': vesement.journal_target.default_credit_account_id.id,
            'move_id': move_id.id,
            'journal_id': vesement.journal_target.id,
            'period_id': move_id.period_id.id,
            'date': vesement.date_vesement,
            'date_maturity': vesement.date_vesement
        }
        line = self.env['account.move.line'].create(move_line)
        return True

    @api.one
    def action_move_line_create(self):
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for vesement in self:
            if vesement.move_id:
                continue
            # Create the account move record.
            move_id = move_pool.create(self.account_move_get(vesement.id)[0])
            vesement.move_id = move_id
            # Create the first line of the vesement
            rec_list_ids = []
            self.first_move_line_get(vesement.id, move_id)
            self.vesement_move_line_create(vesement.id, move_id)
        return True

    @api.multi
    def button_validate(self):
        self.amount_in_word = amount_to_text(self.amount, lang='fr', currency='Dinars')
        self.state = 'valid'
        self.action_move_line_create()
        return True

    @api.one
    def button_cancel(self):
        self.move_id.button_cancel()
        self.move_id.unlink()
        self.state = 'cancel'
        return True

class account_withdrawal_cash(models.Model):
    _name = "account.withdrawal.cash"
    _description = 'Cash Withdrawal'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Reference', copy=False, readonly=True, select=True)
    date_withdrawal = fields.Date(string='Withdrawal Date', default = lambda *a: time.strftime('%Y-%m-%d'),
        readonly=True, states={'draft': [('readonly', False)]}, copy=False)
    journal_target = fields.Many2one('account.journal', 'Journal Target', readonly=True, states={'draft':[('readonly',False)]}, domain=[('type', '=', 'cash')])
    number = fields.Char('Number', required=1, readonly=True, states={'draft':[('readonly', False)]},)
    bank_source = fields.Many2one('res.partner.bank', 'Target Bank', readonly=True, states={'draft':[('readonly', False)]}, domain=[('company_id', '<>', False)])
    journal_source = fields.Many2one('account.journal', 'Journal Source', readonly=True, states={'draft':[('readonly',False)]}, domain=[('type', '=', 'bank')])
    amount = fields.Float(string='Total', digits=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]})
    amount_in_word = fields.Char("Amount in Word")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, readonly=True, states={'draft':[('readonly',False)]})
    move_id = fields.Many2one('account.move', 'Account Entry', copy=False)
    move_ids = fields.One2many(related='move_id.line_id', relation='account.move.line', string='Journal Items', readonly=True)
    note = fields.Text('Notes')
    state = fields.Selection([
                                ('draft', 'Open'),
                                ('valid', 'Validate'),
                                ('cancel', 'Cancel'),
                                ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')

    def onchange_bank(self, cr, uid, ids, bank_source, context=None):
        if context is None:
            context = {}
        if not bank_source:
            return {}
        bank = self.pool.get('res.partner.bank').browse(cr, uid, bank_source)
        return {'value': {'journal_source': bank.journal_id.id}}

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'account.withdrawal', context=context) or '/'
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(account_withdrawal_cash, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("Withdrawal created"), context=ctx)
        return new_id

    @api.multi
    def unlink(self):
        for withdrawal in self:
            if withdrawal.state != 'draft':
                raise osv.except_osv(_('Warning!'), _('You cannot delete this cash withdrawal !'))
        return super(account_withdrawal_cash, self).unlink()

    def button_draft(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'draft'}, context=context)

    @api.one
    def account_move_get(self, withdrawal_id):
        seq_obj = self.pool.get('ir.sequence')
        period_obj = self.env['account.period']
        withdrawal = self.browse(withdrawal_id)
        if withdrawal.journal_target.sequence_id:
            if not withdrawal.journal_target.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            period = period_obj.find(dt=self.date_withdrawal, context=self._context)[0]
            c = dict(self._context)
            c.update({'fiscalyear_id': period.fiscalyear_id.id, 'period_id': period.id})
            name = seq_obj.next_by_id(self._cr, self._uid, withdrawal.journal_target.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))

        ctx = self._context.copy()
        ctx.update({'company_id': withdrawal.company_id.id})
        period_ids = period_obj.find(dt=self._context.get('date', False), context=ctx)
        period_id = period_ids and period_ids[0] or False

        move = {
            'name': name,
            'journal_id': withdrawal.journal_target.id,
            'date': withdrawal.date_withdrawal,
            'ref': name,
            'period_id': period_id.id,
        }
        return move

    @api.one
    def first_move_line_get(self, withdrawal_id, move_id):
        withdrawal = self.browse(withdrawal_id)
        move_line = {
            'name': withdrawal.name or '/',
            'debit': 0,
            'credit': withdrawal.amount,
            'account_id': withdrawal.journal_source.default_debit_account_id.id,
            'move_id': move_id.id,
            'journal_id': withdrawal.journal_target.id,
            'period_id': move_id.period_id.id,
            'date': withdrawal.date_withdrawal,
            'date_maturity': withdrawal.date_withdrawal
        }
        line = self.env['account.move.line'].create(move_line)
        return move_line

    @api.one
    def withdrawal_move_line_create(self, withdrawal_id, move_id):
        rec_lst_ids = []
        withdrawal = self.browse(withdrawal_id)
        move_line = {
            'name': withdrawal.name or '/',
            'debit': withdrawal.amount,
            'credit': 0,
            'account_id': withdrawal.journal_target.default_credit_account_id.id,
            'move_id': move_id.id,
            'journal_id': withdrawal.journal_target.id,
            'period_id': move_id.period_id.id,
            'date': withdrawal.date_withdrawal,
            'date_maturity': withdrawal.date_withdrawal
        }
        line = self.env['account.move.line'].create(move_line)
        return True

    @api.one
    def action_move_line_create(self):
        move_pool = self.env['account.move']
        move_line_pool = self.env['account.move.line']
        for withdrawal in self:
            if withdrawal.move_id:
                continue
            # Create the account move record.
            move_id = move_pool.create(self.account_move_get(withdrawal.id)[0])
            withdrawal.move_id = move_id
            # Create the first line of the withdrawal
            rec_list_ids = []
            self.first_move_line_get(withdrawal.id, move_id)
            self.withdrawal_move_line_create(withdrawal.id, move_id)
        return True

    @api.multi
    def button_validate(self):
        self.amount_in_word = amount_to_text(self.amount, lang='fr', currency='Dinars')
        self.state = 'valid'
        self.action_move_line_create()
        return True

    @api.one
    def button_cancel(self):
        self.move_id.button_cancel()
        self.move_id.unlink()
        self.state = 'cancel'
        return True