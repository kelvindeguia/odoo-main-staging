# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentStatusSelection(models.Model):
    _name = "hr.recruitment.status.selection"
    _description = "Status Selection"
    _rec_name = 'name'

    name = fields.Char('Status Name', store=True)