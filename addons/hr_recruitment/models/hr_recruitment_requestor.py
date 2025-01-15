# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentRequestor(models.Model):
    _name = "hr.recruitment.requestor"
    _description = "Requestor"
    _rec_name = 'name'

    name = fields.Char('Requestor Name', store=True)