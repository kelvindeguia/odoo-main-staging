# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class PhoneDetails(models.Model):
    _name = 'phone.details'
    _description = 'Phone Details'

    phone_id = fields.Char(string='Phone ID')
    label = fields.Char(string='Label')
    value = fields.Char(string='Value')
    partner_id = fields.Many2one('res.partner', string='Partner')
