# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class EmailDetails(models.Model):
    _name = 'email.details'
    _description = 'Email Details'

    email_id = fields.Char(string='Email ID')
    label = fields.Char(string='Label')
    value = fields.Char(string='Value')
    partner_id = fields.Many2one('res.partner', string='Partner')
