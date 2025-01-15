# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentSourcer(models.Model):
    _name = "hr.recruitment.sourcer"
    _description = "Sourcer"
    _rec_name = 'name'

    name = fields.Char('Sourcer Name', store=True)