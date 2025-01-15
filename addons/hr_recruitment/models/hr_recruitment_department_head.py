# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentDepartmentHead(models.Model):
    _name = "hr.recruitment.head"
    _description = "Department Head"
    _rec_name = 'name'

    name = fields.Char('Department Name', store=True)