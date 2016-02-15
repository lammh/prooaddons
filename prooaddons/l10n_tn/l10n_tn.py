# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013 Open vision (http://www.openvision.tn).
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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class l10n_tn_report(osv.osv):
    _name = 'l10n.tn.report'
    _description = 'Report for l10n_tn'
    _columns = {
        'code': fields.char('Code', size=64),
        'name': fields.char('Name', size=128),
        'line_ids': fields.one2many('l10n.tn.line', 'report_id', 'Lines'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)','The code report must be unique !')
    ]

l10n_tn_report()

class l10n_tn_line(osv.osv):
    _name = 'l10n.tn.line'
    _description = 'Report Lines for l10n_tn'
    _columns = {
        'code': fields.char('Variable Name', size=64),
        'definition': fields.char('Definition', size=512),
        'name': fields.char('Name', size=256),
        'report_id': fields.many2one('l10n.tn.report', 'Report'),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The variable name must be unique !')
    ]

l10n_tn_line()

class account_journal(osv.osv):
    _inherit = 'account.journal'

    _columns={
        'type': fields.selection([('sale', 'Sale'),('sale_refund','Sale Refund'), ('purchase', 'Purchase'), ('purchase_refund','Purchase Refund'), ('cash', 'Cash'), ('bank', 'Bank and Checks'), ('general', 'General'), ('situation', 'Opening/Closing Situation'), ('withholding_sale', 'Withholding Sale'), ('withholding_purchase', 'Withholding Purchase')], 'Type', size=32, required=True,
                                 help="Select 'Sale' for customer invoices journals."\
                                 " Select 'Purchase' for supplier invoices journals."\
                                 " Select 'Cash' or 'Bank' for journals that are used in customer or supplier payments."\
                                 " Select 'General' for miscellaneous operations journals."\
                                 " Select 'Opening/Closing Situation' for entries generated for new fiscal years."),
             }
account_journal()

class taxes(osv.osv):
    _inherit = 'account.tax.template'

    _columns = {
        'stamp': fields.boolean('Tax Stamp'),
        'is_wht': fields.boolean('Withholding Tax'),
        'withholding_amount': fields.float('Withholding Amount', digits_compute=dp.get_precision('Product Price')),
        'fodec': fields.boolean('FODEC'),
    }

    def _generate_tax(self, cr, uid, tax_templates, tax_code_template_ref, company_id, context=None):
        """
        This method generate taxes from templates.

        :param tax_templates: list of browse record of the tax templates to process
        :param tax_code_template_ref: Taxcode templates reference.
        :param company_id: id of the company the wizard is running for
        :returns:
            {
            'tax_template_to_tax': mapping between tax template and the newly generated taxes corresponding,
            'account_dict': dictionary containing a to-do list with all the accounts to assign on new taxes
            }
        """
        if context is None:
            context = {}
        res = {}
        todo_dict = {}
        tax_template_to_tax = {}
        for tax in tax_templates:
            vals_tax = {
                'name':tax.name,
                'sequence': tax.sequence,
                'amount': tax.amount,
                'type': tax.type,
                'applicable_type': tax.applicable_type,
                'domain': tax.domain,
                'parent_id': tax.parent_id and ((tax.parent_id.id in tax_template_to_tax) and tax_template_to_tax[tax.parent_id.id]) or False,
                'child_depend': tax.child_depend,
                'python_compute': tax.python_compute,
                'python_compute_inv': tax.python_compute_inv,
                'python_applicable': tax.python_applicable,
                'base_code_id': tax.base_code_id and ((tax.base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.base_code_id.id]) or False,
                'tax_code_id': tax.tax_code_id and ((tax.tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.tax_code_id.id]) or False,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_code_id': tax.ref_base_code_id and ((tax.ref_base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_base_code_id.id]) or False,
                'ref_tax_code_id': tax.ref_tax_code_id and ((tax.ref_tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_tax_code_id.id]) or False,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'include_base_amount': tax.include_base_amount,
                'description': tax.description,
                'company_id': company_id,
                'type_tax_use': tax.type_tax_use,
                'price_include': tax.price_include,
                'stamp': tax.stamp,
                'fodec': tax.fodec,
            }
            new_tax = self.pool.get('account.tax').create(cr, uid, vals_tax)
            tax_template_to_tax[tax.id] = new_tax
            #as the accounts have not been created yet, we have to wait before filling these fields
            todo_dict[new_tax] = {
                'account_collected_id': tax.account_collected_id and tax.account_collected_id.id or False,
                'account_paid_id': tax.account_paid_id and tax.account_paid_id.id or False,
            }
        res.update({'tax_template_to_tax': tax_template_to_tax, 'account_dict': todo_dict})
        return res

class taxes(osv.osv):
    _inherit = 'account.tax'

    _columns = {
        'stamp': fields.boolean('Tax Stamp'),
        'is_wht': fields.boolean('Withholding Tax'),
        'withholding_amount': fields.float('Withholding Amount', digits_compute=dp.get_precision('Product Price')),
        'fodec': fields.boolean('FODEC'),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
