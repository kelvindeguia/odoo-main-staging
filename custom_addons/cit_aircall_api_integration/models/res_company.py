# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    number_config_ids = fields.Many2many(
        "number.number",
        string="Numbers",
    )
    number_crm_config_ids = fields.Many2many(
        "number.number",
        relation='number_number_crm_res_company_rel',
        string="Numbers",
    )
    number_helpdesk_config_ids = fields.Many2many(
        "number.number",
        relation='number_number_helpdesk_res_company_rel',
        string="Numbers",
    )
