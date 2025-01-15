# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models


class AircallDetails(models.Model):
    _name = 'aircall.details'
    _description = 'Aircall Connection'
    _rec_name = 'customer_id'

    call_by_user = fields.Char(string='By User')
    # recording_attachment_id = fields.Many2one('ir.attachment',
    #                                           string='Audio Attachment'
    #                                           )
    recording_url = fields.Char(string='Recording')
    customer_id = fields.Many2one('res.partner', string='Contact Name')
    phonenumbers = fields.Char(string="Phone Number")
    call_qualification = fields.Char(string="Call Type")
    call_duration = fields.Char(string="Call Duration")
    waiting_time = fields.Char(string="Waiting Time")
    call_time = fields.Char(string="Call Time")
    air_call_number = fields.Char(string="Aircall number")
    tags = fields.Char(string="Tags")
    notes = fields.Char(string="Notes")
    aircall_call_id = fields.Char(string='Air Call Log ID')

    def name_get(self):
        res = []
        for record in self:
            if self.customer_id:
                partner = self.customer_id.name
            else:
                partner = ''
            storer_patner_name = (
                    str('call with ') + partner
            )
            res.append((record.id, storer_patner_name))
        return res
