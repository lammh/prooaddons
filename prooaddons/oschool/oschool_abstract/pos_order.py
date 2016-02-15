# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class pos_order(models.Model):
    _inherit = 'pos.order'

    type = fields.Char('type')
