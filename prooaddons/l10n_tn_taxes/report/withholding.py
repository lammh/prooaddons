# -*- coding: utf-8 -*-

import time
from openerp.report import report_sxw

class withholding(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(withholding, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
        })

report_sxw.report_sxw('report.withholding', 'account.voucher', 'l10n_tn_taxes/report/withholding.rml', parser=withholding, header="external")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

