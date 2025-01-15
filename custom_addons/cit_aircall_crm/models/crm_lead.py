# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    add_log_note = fields.Boolean(string="Add Log Note", default=False)
