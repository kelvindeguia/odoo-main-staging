# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentSpecificSource(models.Model):
    _name = "hr.recruitment.specific.source"
    _description = "Specific Source"
    _rec_name = 'name'

    name = fields.Char('Source Name', store=True)
    channel_id = fields.Many2one('hr.recruitment.channel', string="Channel", store=True)