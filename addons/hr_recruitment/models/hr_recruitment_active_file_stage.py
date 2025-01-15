# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentActiveFileStage(models.Model):
    _name = "hr.recruitment.active.file.stage"
    _description = "Active File Stage"
    _rec_name = 'name'

    name = fields.Char('Stage Name', store=True)