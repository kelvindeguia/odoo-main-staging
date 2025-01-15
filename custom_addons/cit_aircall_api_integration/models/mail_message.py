# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

from odoo import fields, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    aircall_call_id = fields.Char(string='Aircall Log ID')
    recording_attachment_id = fields.Many2one(
        'ir.attachment',  string='Audio Recording', ondelete='set null', readonly=True)
