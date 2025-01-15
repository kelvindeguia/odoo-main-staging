# -*- coding: utf-8 -*-

from odoo import fields, models

class JobApplication(models.Model):
    _name = "hr.job.application"
    _description = "Job Application"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = "name"

    active = fields.Boolean(string="Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    name = fields.Char(string='Applicant Name', store=True)
    email = fields.Char(string='Email', store=True)
    mobile_number = fields.Char(string='Mobile Number', store=True)
    attachment_id = fields.Many2many(comodel_name='ir.attachment',
                                    relation='m2m_ir_form_rel',
                                    column1='m2m_id',
                                    column2='attachment_id',
                                    string='Resume/CV')
    linkedin = fields.Char(string="LinkedIn Profile", store=True)
    requisition_id = fields.Many2one('hr.requisition', string="Requisition ID", store=True)
    status = fields.Selection([('untapped','Untapped'),('dispatched','Dispatched')], string="Status", default='untapped', store=True)
    dispatch_date = fields.Datetime(string="Dispatch Date")
    # record_ageing = fields.Integer('Record Ageing', compute="_compute_record_ageing")
    record_ageing = fields.Integer(string='Record Ageing')
    record_ageing_ref = fields.Integer(string='Record Ageing Reference', store=True)
    # date_today = fields.Datetime("Datetime Today", compute="_compute_date_today")
    date_today = fields.Datetime(string="Datetime Today")
    update_logs = fields.Text(string="Fields Update Logs", store=True)
    user_id = fields.Many2one('res.users', string='User')
