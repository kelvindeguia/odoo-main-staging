# -*- coding: utf-8 -*-

from odoo import fields, models

class Pooling(models.Model):
    _name = "hr.pooling"
    _description = "For Pooling"
    _rec_name = "name"

    active = fields.Boolean(string="Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    name = fields.Char(string='Applicant Name', store=True)
    email = fields.Char(string='Email', store=True)
    priority = fields.Char(string='Priority', store=True)
    mobile_number = fields.Char(string='Mobile Number', store=True)
    attachment_id = fields.Many2many(comodel_name='ir.attachment',
                                     relation='m2m_ir_pooling_rel',
                                     column1='m2m_id',
                                     column2='attachment_id',
                                     string='CV')
    linkedin = fields.Char(string="LinkedIn Profile", store=True)
    requisition_id = fields.Many2one('hr.requisition', string="Requisition ID", store=True)
    # dept_name = fields.Char(string='Client Name', related='requisition_id.department_id.name')
    dept_name = fields.Char(string='Client Name')
    # job_title_name = fields.Char(string='Job Title', readonly=True, related='requisition_id.job_id.name')
    job_title_name = fields.Char(string='Job Title', readonly=True)
    status = fields.Selection([('untapped', 'Untapped'), ('dispatched_applicants', 'Dispatched to All Applicants'), 
                               ('dispatched_portal', 'Dispatched to Job Portal')], string="Status", default='untapped', store=True)
    dispatch_date = fields.Datetime(string="Dispatch Date")
    record_ageing = fields.Integer(string='Record Ageing')
    # record_ageing = fields.Integer('Record Ageing', compute="_compute_record_ageing")
    record_ageing_ref = fields.Integer(string='Record Ageing Reference', store=True)
    # date_today = fields.Datetime("Datetime Today", compute="_compute_date_today")
    date_today = fields.Datetime(string="Datetime Today")
    remarks = fields.Text(string='Remarks', store=True)
    update_logs = fields.Text(string="Fields Update Logs", store=True)
    user_id = fields.Many2one('res.users', string='User')
    specific_source_id = fields.Many2one('hr.recruitment.specific.source', string='Specific Source', store=True)
    channel_id = fields.Many2one('hr.recruitment.channel', string="Channel", store=True)
    received_date = fields.Date(string='Received Date', store=True)
    specific_source_ref = fields.Char(string="Admin Field", store=True)
    profile_link = fields.Char(string='Profile Link', store=True)