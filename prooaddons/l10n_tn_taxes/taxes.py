from openerp import models, fields, api, _
from amount_to_text_fr import amount_to_text


class taxes_client(models.Model):
    _inherit = 'res.partner'

    stamp_exemption = fields.Boolean('Stamp Tax Exemption')
    vat_exemption = fields.Boolean('VAT Exemption')
    fodec = fields.Boolean('FODEC')
    partner_registry = fields.Char('Partner Registry',size=64)

taxes_client()

class account_invoice(models.Model):
    _inherit = 'account.invoice'
    
    amount_in_word = fields.Char("Amount in Word" , size=500)

    @api.multi
    def button_reset_taxes(self):
        account_invoice_tax = self.env['account.invoice.tax']
        ctx = dict(self._context)
        for invoice in self:
            self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (invoice.id,))
            self.invalidate_cache()
            partner = invoice.partner_id
            invoice.amount_in_word = amount_to_text(invoice.amount_total, lang='fr', currency='Dinars')
            if partner.lang:
                ctx['lang'] = partner.lang
            for taxe in account_invoice_tax.compute(invoice.with_context(ctx)).values():
                account_invoice_tax.create(taxe)
        # dummy write on self to trigger recomputations
        return self.with_context(ctx).write({'invoice_line': []})

class account_tax(models.Model):
    _inherit = 'account.tax'

    @api.v8
    def compute_all(self, price_unit, quantity, product=None, partner=None, force_excluded=False):
        return self._model.compute_all(
            self._cr, self._uid, self, price_unit, quantity,
            product=product, partner=partner, force_excluded=force_excluded)

    @api.v7
    def compute_all(self, cr, uid, taxes, price_unit, quantity, product=None, partner=None, force_excluded=False):
        """
        :param force_excluded: boolean used to say that we don't want to consider the value of field price_include of
            tax. It's used in encoding by line where you don't matter if you encoded a tax with that boolean to True or
            False
        RETURN: {
                'total': 0.0,                # Total without taxes
                'total_included: 0.0,        # Total with taxes
                'taxes': []                  # List of taxes, see compute for the format
            }
        """
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        tax_compute_precision = precision
        if taxes and taxes[0].company_id.tax_calculation_rounding_method == 'round_globally':
            tax_compute_precision += 5
        totalin = totalex = round(price_unit * quantity, precision)
        tin = []
        tex = []
        if partner:
            obj_partner=self.pool.get('res.partner').browse(cr, uid, partner.id, context=None)
            if obj_partner.vat_exemption:
                return {
                    'total': totalex,
                    'total_included': totalin,
                    'taxes': {},
                }
        for tax in taxes:
            if not tax.price_include or force_excluded:
                tex.append(tax)
            else:
                tin.append(tax)
        tin = self.compute_inv(cr, uid, tin, price_unit, quantity, product=product, partner=partner, precision=tax_compute_precision)
        for r in tin:
            totalex -= r.get('amount', 0.0)
        totlex_qty = 0.0
        try:
            totlex_qty = totalex/quantity
        except:
            pass
        tex = self._compute(cr, uid, tex, totlex_qty, quantity, product=product, partner=partner, precision=tax_compute_precision)
        for r in tex:
            totalin += r.get('amount', 0.0)
        return {
            'total': totalex,
            'total_included': totalin,
            'taxes': tin + tex
        }

class account_invoice_tax(models.Model):
    _inherit = 'account.invoice.tax'

    @api.v8
    def compute(self, invoice):
        tax_grouped = {}
        currency = invoice.currency_id.with_context(date=invoice.date_invoice or fields.Date.context_today(invoice))
        company_currency = invoice.company_id.currency_id
        for line in invoice.invoice_line:
            taxes = line.invoice_line_tax_id.compute_all(
                (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                line.quantity, line.product_id, invoice.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': invoice.id,
                    'name': tax['name'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'base': currency.round(tax['price_unit'] * line['quantity']),
                }
                if invoice.type in ('out_invoice','in_invoice'):
                    val['base_code_id'] = tax['base_code_id']
                    val['tax_code_id'] = tax['tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_collected_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_collected_id']
                else:
                    val['base_code_id'] = tax['ref_base_code_id']
                    val['tax_code_id'] = tax['ref_tax_code_id']
                    val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                    val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                    val['account_id'] = tax['account_paid_id'] or line.account_id.id
                    val['account_analytic_id'] = tax['account_analytic_paid_id']

                # If the taxes generate moves on the same financial account as the invoice line
                # and no default analytic account is defined at the tax level, propagate the
                # analytic account from the invoice line to the tax line. This is necessary
                # in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
                if not key in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['base'] += val['base']
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base_amount'] += val['base_amount']
                    tax_grouped[key]['tax_amount'] += val['tax_amount']

        # Insertion timbre fiscale dans la facture
        if not invoice.partner_id.stamp_exemption:
            if invoice.type in ('in_invoice', 'in_refund'):
                timbre = self.env['account.tax'].search([('stamp','=',True), ('type_tax_use', '=', 'purchase')], limit=1)
            else:
                timbre = self.env['account.tax'].search([('stamp','=',True), ('type_tax_use', '=', 'sale')], limit=1)
    
            if not timbre:
                raise Warning(_('No tax stamp tax types.'))

            val = {
                    'invoice_id': invoice.id,
                    'name': timbre.name,
                    'amount': timbre.amount,
                    'manual': False,
                    'sequence': timbre.sequence,
                    'base': 0,
                    'base_amount': 0,
                    'tax_amount': currency.compute(timbre.amount * timbre.tax_sign, company_currency, round=False)
                }

            if invoice.type in ('out_invoice','in_invoice'):
                val['base_code_id'] = timbre.base_code_id.id
                val['tax_code_id'] = timbre.tax_code_id.id
                val['account_id'] = timbre.account_collected_id.id or line.account_id.id
                val['account_analytic_id'] = timbre.account_analytic_collected_id.id or False
            else:
                val['base_code_id'] = timbre.ref_base_code_id.id
                val['tax_code_id'] = timbre.ref_tax_code_id.id
                val['account_id'] = timbre.account_paid_id.id or line.account_id.id
                val['account_analytic_id'] = timbre.account_analytic_paid_id.id or False

            key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
            if not key in tax_grouped:
                tax_grouped[key] = val
            else:
                tax_grouped[key]['amount'] += val['amount']
                tax_grouped[key]['base'] += val['base']
                tax_grouped[key]['base_amount'] += val['base_amount']
                tax_grouped[key]['tax_amount'] += val['tax_amount']

        for t in tax_grouped.values():
            t['base'] = currency.round(t['base'])
            t['amount'] = currency.round(t['amount'])
            t['base_amount'] = currency.round(t['base_amount'])
            t['tax_amount'] = currency.round(t['tax_amount'])

        return tax_grouped

account_invoice_tax()
