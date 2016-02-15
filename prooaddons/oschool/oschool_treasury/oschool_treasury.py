# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
import time
from openerp.osv import osv

class oschool_treasury(models.Model):

    _inherit = "account.treasury"

    statement_id = fields.Many2one('account.bank.statement.line', ondelete='cascade')
    pos_order = fields.Many2one('pos.order', ondelete='cascade')


class oschool_make_payement(models.Model):
    _inherit = 'pos.make.payment'

    journal_id = fields.Many2one('account.journal', string='Payment Mode', required=True,
                                 domain="[('type', 'in', ['bank', 'cash'])]")
    is_check = fields.Boolean(related='journal_id.is_check')
    check_number = fields.Char(string='Check number')
    check_holder = fields.Char(string='Check holder')
    bank_source = fields.Many2one('res.bank',string='Bank Source')
    check_creation_date = fields.Date(string='Creation Date')
    check_reception_date = fields.Date(string='Reception Date')
    check_due_date = fields.Date(string='Due Date')
    is_warranty_check = fields.Boolean(string="Warranty check")


    def create(self, cr, uid, vals, context=None):
        return_id = super(oschool_make_payement, self).create(cr, uid, vals, context=context)
        if vals['is_check']:
            current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            order_obj = self.pool.get('pos.order')
            active_id = context and context.get('active_id', False)
            order = order_obj.browse(cr, uid, active_id, context=context)
            state = 'draft'
            if vals['is_warranty_check']:
                state = 'warranty'
            treasury_obj = self.pool.get('account.treasury')
            treasury_obj.create(cr, uid, {
               "name": vals['check_number'],
               "partner_id": order.partner_id.id,
               "user_id" : uid,
               "company_id": current_user.company_id.id,
               "state": state,
               'type':'ch',
               'emission_date': vals['check_creation_date'],
               'type_transaction': 'receipt',
               'holder': vals['check_holder'],
               'reception_date': vals['check_reception_date'],
               'bank_source': vals['bank_source'],
               'amount': vals['amount'],
               'clearing_date': vals['check_due_date'],
               # 'statement_id': context.get('treasury_statement_id'), # a corriger
               'pos_order': active_id,
            }, context=context)
        return return_id




class oschool_account_bank_statement_line(models.Model):
    _inherit = 'account.bank.statement.line'
    check_number = fields.Char(string='Check number')

class oschool_pos_order(models.Model):

    _inherit = 'pos.order'

    def add_payment(self, cr, uid, order_id, data, context=None):
        """Create a new payment for the order"""
        context = dict(context or {})
        statement_line_obj = self.pool.get('account.bank.statement.line')
        property_obj = self.pool.get('ir.property')
        order = self.browse(cr, uid, order_id, context=context)
        args = {
            'amount': data['amount'],
            'date': data.get('payment_date', time.strftime('%Y-%m-%d')),
            'name': order.name + ': ' + (data.get('payment_name', '') or ''),
            'partner_id': order.partner_id and self.pool.get("res.partner")._find_accounting_partner(order.partner_id).id or False,
            'check_number': data.get('check_number', ''),
        }

        journal_id = data.get('journal', False)
        statement_id = data.get('statement_id', False)
        assert journal_id or statement_id, "No statement_id or journal_id passed to the method!"

        journal = self.pool['account.journal'].browse(cr, uid, journal_id, context=context)
        # use the company of the journal and not of the current user
        company_cxt = dict(context, force_company=journal.company_id.id)
        account_def = property_obj.get(cr, uid, 'property_account_receivable', 'res.partner', context=company_cxt)
        args['account_id'] = (order.partner_id and order.partner_id.property_account_receivable \
                             and order.partner_id.property_account_receivable.id) or (account_def and account_def.id) or False

        if not args['account_id']:
            if not args['partner_id']:
                msg = _('There is no receivable account defined to make payment.')
            else:
                msg = _('There is no receivable account defined to make payment for the partner: "%s" (id:%d).') % (order.partner_id.name, order.partner_id.id,)
            raise osv.except_osv(_('Configuration Error!'), msg)

        context.pop('pos_session_id', False)

        for statement in order.session_id.statement_ids:
            if statement.id == statement_id:
                journal_id = statement.journal_id.id
                break
            elif statement.journal_id.id == journal_id:
                statement_id = statement.id
                break

        if not statement_id:
            raise osv.except_osv(_('Error!'), _('You have to open at least one cashbox.'))

        args.update({
            'statement_id': statement_id,
            'pos_statement_id': order_id,
            'journal_id': journal_id,
            'ref': order.session_id.name,
        })

        statement_line_obj.create(cr, uid, args, context=context)

        # return {'context':{'treasury_statement_id':statement_id}, 'statement_id':statement_id}
        # self.localcontext.update({'treasury_statement_id':statement_id})
        return statement_id