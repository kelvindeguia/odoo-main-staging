# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentChannel(models.Model):
    _name = "hr.recruitment.channel"
    _description = "Channel"
    _rec_name = 'name'

    name = fields.Char('Channel Name', store=True)