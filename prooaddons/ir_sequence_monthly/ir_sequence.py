# -*- coding: utf-8 -*-
##############################################################################
#
#    Auto reset sequence by year,month,day
#    Copyright 2013 wangbuke <wangbuke@gmail.com>
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
from openerp.tools.translate import _
from openerp import api
import time
from datetime import datetime

class ir_sequence(osv.osv):
    _inherit = 'ir.sequence'

    _columns = {
        'monthly': fields.boolean('Monthly'),
        'january': fields.integer('January', required=True),
        'february': fields.integer('February', required=True),
        'march': fields.integer('March', required=True),
        'april': fields.integer('April', required=True),
        'may': fields.integer('May', required=True),
        'june': fields.integer('June', required=True),
        'july': fields.integer('July', required=True),
        'august': fields.integer('August', required=True),
        'september': fields.integer('September', required=True),
        'october': fields.integer('October', required=True),
        'november': fields.integer('November', required=True),
        'december': fields.integer('December', required=True),
    }

    _defaults = {
        'monthly': False,
        'january': 1,
        'february': 1,
        'march': 1,
        'april': 1,
        'may': 1,
        'june': 1,
        'july': 1,
        'august': 1,
        'september': 1,
        'october': 1,
        'november': 1,
        'december': 1,
    }

    def _interpolation_dict2(self, period):
        t = time.localtime() # Actually, the server is always in UTC.
        return {
            'year': time.strftime('%Y', t),
            'month': period,
            'day': time.strftime('%d', t),
            'y': time.strftime('%y', t),
            'doy': time.strftime('%j', t),
            'woy': time.strftime('%W', t),
            'weekday': time.strftime('%w', t),
            'h24': time.strftime('%H', t),
            'h12': time.strftime('%I', t),
            'min': time.strftime('%M', t),
            'sec': time.strftime('%S', t),
        }

    @api.cr_uid_ids_context
    def _next(self, cr, uid, ids, context=None):
        if not ids:
            return False
        if context is None:
            context = {}
        force_company = context.get('force_company')
        if not force_company:
            force_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        for seq in self.browse(cr, uid, ids, context):
            for line in seq.fiscal_ids:
                if line.fiscalyear_id.id == context.get('fiscalyear_id'):
                    ids = [line.sequence_id.id]
        sequences = self.read(cr, uid, ids, ['name', 'company_id', 'implementation', 'number_next', 'prefix', 'suffix', 'padding', 'monthly',
                                             'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])
        preferred_sequences = [s for s in sequences if s['company_id'] and s['company_id'][0] == force_company ]
        seq = preferred_sequences[0] if preferred_sequences else sequences[0]
        if seq['implementation'] == 'standard':
            if seq['monthly']:
                period_id = self.pool.get('account.period').browse(cr, uid, context.get('period_id'))
                date_start = datetime.strptime(period_id.date_start, "%Y-%m-%d")
                period = date_start.strftime('%m')
                if period == '01':
                    seq['number_next'] = seq['january']
                    cr.execute("UPDATE ir_sequence SET january=january+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '02':
                    seq['number_next'] = seq['february']
                    cr.execute("UPDATE ir_sequence SET february=february+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '03':
                    seq['number_next'] = seq['march']
                    cr.execute("UPDATE ir_sequence SET march=march+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '04':
                    seq['number_next'] = seq['april']
                    cr.execute("UPDATE ir_sequence SET april=april+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '05':
                    seq['number_next'] = seq['may']
                    cr.execute("UPDATE ir_sequence SET may=may+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '06':
                    seq['number_next'] = seq['june']
                    cr.execute("UPDATE ir_sequence SET june=june+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '07':
                    seq['number_next'] = seq['july']
                    cr.execute("UPDATE ir_sequence SET july=july+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '08':
                    seq['number_next'] = seq['august']
                    cr.execute("UPDATE ir_sequence SET august=august+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '09':
                    seq['number_next'] = seq['september']
                    cr.execute("UPDATE ir_sequence SET september=september+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '10':
                    seq['number_next'] = seq['october']
                    cr.execute("UPDATE ir_sequence SET october=october+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '11':
                    seq['number_next'] = seq['november']
                    cr.execute("UPDATE ir_sequence SET november=november+number_increment WHERE id=%s ", (seq['id'],))
                elif period == '12':
                    seq['number_next'] = seq['december']
                    cr.execute("UPDATE ir_sequence SET december=december+number_increment WHERE id=%s ", (seq['id'],))

            else:
                cr.execute("SELECT nextval('ir_sequence_%03d')" % seq['id'])
                seq['number_next'] = cr.fetchone()
        else:
            cr.execute("SELECT number_next FROM ir_sequence WHERE id=%s FOR UPDATE NOWAIT", (seq['id'],))
            cr.execute("UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s ", (seq['id'],))
            self.invalidate_cache(cr, uid, ['number_next'], [seq['id']], context=context)
        if seq['monthly']:
            d = self._interpolation_dict2(period)
        else:
            d = self._interpolation_dict()
        try:
            interpolated_prefix = self._interpolate(seq['prefix'], d)
            interpolated_suffix = self._interpolate(seq['suffix'], d)
        except ValueError:
            raise osv.except_osv(_('Warning'), _('Invalid prefix or suffix for sequence \'%s\'') % (seq.get('name')))
        return interpolated_prefix + '%%0%sd' % seq['padding'] % seq['number_next'] + interpolated_suffix

class account_move(osv.osv):
    _inherit = "account.move"

    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)

        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id, 'period_id': move.period_id.id}
                        new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})

        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))
        self.invalidate_cache(cr, uid, context=context)
        return True

class account_voucher(osv.osv):
    _inherit = "account.voucher"

    def account_move_get(self, cr, uid, voucher_id, context=None):
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id, 'period_id': voucher.period_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
        }
        return move

class account_bank_statement(osv.osv):

    _inherit = "account.bank.statement"

    def _compute_default_statement_name(self, cr, uid, journal_id, context=None):
        context = dict(context or {})
        obj_seq = self.pool.get('ir.sequence')
        period = self.pool.get('account.period').browse(cr, uid, self._get_period(cr, uid, context=context), context=context)
        context['fiscalyear_id'] = period.fiscalyear_id.id
        context['period_id'] = period.id
        journal = self.pool.get('account.journal').browse(cr, uid, journal_id, None)
        return obj_seq.next_by_id(cr, uid, journal.sequence_id.id, context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
