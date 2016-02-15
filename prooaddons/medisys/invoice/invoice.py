from openerp import models,fields


class InvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    date = fields.Datetime(string='Date')

    def create(self, cr, uid, values, context=None):
        values['date'] = fields.Datetime.now()
        return super(InvoiceLine, self).create(cr, uid, values, context=context)


