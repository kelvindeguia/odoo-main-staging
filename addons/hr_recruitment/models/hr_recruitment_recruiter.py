# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentRecruiter(models.Model):
    _name = "hr.recruitment.recruiter"
    _description = "Recruiter"
    _rec_name = 'name'

    name = fields.Char('Recruiter', store=True)