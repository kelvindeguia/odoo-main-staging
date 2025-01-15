# -*- coding: utf-8 -*-

from odoo import fields, models

class RecruitmentStageLogs(models.Model):
    _name = "hr.recruitment.stage.logs"
    _description = "Stage Logs"
    _rec_name = 'name'

    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.", index=True)

    name = fields.Char('Name', store=True)
    record_id = fields.Many2one('hr.applicant', string="Record", store=True)
    old_stage = fields.Char(string="Old Stage", store=True)
    new_stage = fields.Char(string="New Stage", store=True)
    initial_date = fields.Datetime(string="Initial Date", store=True)
    changed_date = fields.Datetime(string="Changed Date", store=True)
    days_duration = fields.Integer(string="Days Duration", store=True)