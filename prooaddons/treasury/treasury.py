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
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields
from openerp.osv import osv
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class treasury_document_type(models.Model):
    _name = "account.treasury.type"

    name = fields.Char('Name', required=True)
    generate = fields.Boolean('Generate Treasury Document', default=True)

class treasury_document(models.Model):
    _name = "account.treasury"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "clearing_date"

    name = fields.Char('Document ID',size=64, select=1, required=True, readonly=True, states={'draft':[('readonly',False)]})
    partner_id = fields.Many2one('res.partner','Partner', required=True, readonly=True,states={'draft':[('readonly',False)]},
                                     help="Partner who made the pay with this document.")
    holder = fields.Char('Holder', size=128, required=True, readonly=True,states={'draft':[('readonly',False)]},
                                     help="Holder who made the pay with this document.")
    user_id = fields.Many2one('res.users','Possessor', required=True, help="User who receive this document.", track_visibility='onchange')
    cashier_id = fields.Many2one('hr.employee', 'Cashier', readonly=True)
    partner_steed = fields.Boolean('Partner Steed', default=True)
    steed_id = fields.Many2one('hr.employee', 'Steed')
    company_id = fields.Many2one('res.company', 'Company', required=True, readonly=True, states={'draft':[('readonly',False)]},
                                     help="Company related to this treasury")
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]}, help="Value of the Treasure")
    reception_date = fields.Date('Reception Date', required=True, readonly=True, states={'draft':[('readonly',False)]})
    clearing_date = fields.Date('Clearing Date', required=True, readonly=True, states={'draft':[('readonly',False)]})
    done_date = fields.Date('Solved Date', readonly=True, states={'clearing':[('readonly',False)],'expected':[('readonly',False)]})
    bank_source = fields.Many2one('res.bank','Source Bank', required=True, readonly=True, states={'draft':[('readonly',False)]})
    bank_target = fields.Many2one('res.partner.bank','Target Bank', readonly=True, states={'draft':[('readonly',False)], 'valid':[('readonly',False),('required',True)]})
    third_party_partner = fields.Many2one('res.partner','3rd Party Partner', readonly=True, states={'draft':[('readonly',False)]},
                                     help="Document coming from or endorsed to a third party partner")
    type = fields.Many2one('account.treasury.type', 'Document Type', required=True, select=1, readonly=True, states={'draft':[('readonly',False)]})
    state = fields.Selection([
                                ('draft', 'Open'),
                                ('valid', 'Valid'),
                                ('warranty', 'Warranty'),
                                ('clearing', 'Clearing'),
                                ('expected', 'Expected'),
                                ('paid', 'Paid'),
                                ('rejected', 'Rejected'),
                                ('notice', 'Notice'),
                                ('cancel', 'Offset'),
                                ], 'State', required=True, readonly=True, select=1, default='draft', track_visibility='onchange')
    note = fields.Text('Notes')
    voucher_ids = fields.Many2many('account.voucher', 'account_voucher_treasury_rel', 'treasury_id', 'voucher_id', 'Associated Vouchers')
    type_transaction = fields.Selection([('receipt', 'Customer payment'), ('payment', 'Supplier payment')], 'Transaction Type', required=True, readonly=True, states={'draft':[('readonly',False)]})

    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    _defaults = {
        'user_id': lambda self, cr, uid, context: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'reception_date': lambda *a: time.strftime('%Y-%m-%d'),
        'partner_id': lambda obj, cr, uid, context: context.get('partner_id', None),
        'amount': lambda obj, cr, uid, context: context.get('amount', None),
        'cashier_id': _employee_get,
        }

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        if context is None:
            context = {}
        if not partner_id:
            return {}
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        if partner.customer:
            type_transaction = 'receipt'
        else:
            type_transaction = 'payment'
        return {'value': {'holder': partner.display_name, 'type_transaction': type_transaction}}

    def unlink(self,cr, uid, ids, context=None):
        for treasury in self.browse(cr, uid, ids, context=context):
            if treasury.state not in ('draft', 'valid', 'cancel'):
                raise osv.except_osv(_('Warning!'),_('You cannot delete this Document !'))
        return super(treasury_document, self).unlink(cr, uid, [ids], context=context)

    def button_validate(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'valid'}, context=context)

    def button_warranty(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'warranty'}, context=context)

    def button_clearing(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'clearing'}, context=context)

    def button_paid(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'paid'}, context=context)

    def button_expected(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'expected'}, context=context)

    def button_notice(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'notice'}, context=context)

    def button_rejected(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'rejected'}, context=context)

    def button_cancel(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'cancel'}, context=context)

    def button_draft(self, cr, user, ids, context=None):
        return self.write(cr, user, ids, {'state': 'draft'}, context=context)

#    def write(self, cr, uid, ids, vals, context=None):
#        if not context:
#            context = {}
#
#        if vals.get('state'):
#            if vals.get('state') == 'valid': state = _('Valid')
#            if vals.get('state') == 'warranty': state = _('Warranty')
#            if vals.get('state') == 'clearing': state = _('Clearing')
#            if vals.get('state') == 'expected': state = _('Expected')
#            if vals.get('state') == 'paid': state = _('Paid')
#            if vals.get('state') == 'notice': state = _('Notice')
#            if vals.get('state') == 'rejected': state = _('Rejected')
#            if vals.get('state') == 'cancel': state = _('Cancelled')
#            if vals.get('state') == 'draft': state = _('Open')
#        return super(treasury_document, self).write(cr, uid, ids, vals, context)


