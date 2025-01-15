# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentManager(models.Model):
    _name = "hr.recruitment.manager"
    _description = "Recruitment Manager"
    _rec_name = 'name'

    name = fields.Char('Recruitment Manager', store=True)