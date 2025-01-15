# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta, timezone
import pandas as pd
import pytz
import numpy as np

class Requisition(models.Model):
    _name = "hr.recruitment.requisition"
    _description = "Requisition"
    _inherit = ['mail.thread']
    _order = 'sequence'
    _rec_name = 'req_id'

    active = fields.Boolean(default=True)
    name = fields.Char(string='Requisition', store=True)
    sequence = fields.Integer(default=10)
    req_id = fields.Char('Requisition ID', readonly=True, store=True)
    
    # Requisition Information Fields
    department_id = fields.Many2one('hr.department', 'Client Name', required=True, store=True)
    job_id = fields.Many2one('hr.job', 'Job Title', required=True, compute="_compute_job_id", readonly=False, store=True)
    # job_id = fields.Many2one('hr.job', string="Job Title", required=True, readonly=False, store=True)
    job_description_ids = fields.Many2many(comodel_name='ir.attachment', 
                                           required=True,
                                           relation='m2m_ir_job_description_ids_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Job Description')
    calibration_notes_ids = fields.Many2many(comodel_name='ir.attachment',
                                    relation='m2m_ir_calibration_notes_ids_rel',
                                    column1='m2m_id',
                                    column2='attachment_id',
                                    string='Calibration Notes')
    company = fields.Selection([('aiic', 'ONSITE (ISUPPORT)'), ('iswerk', 'ONSITE (ISWERK)'),
                                ('iswerk_hybrid', 'Hybrid (ISWERK)'), ('iswerk_wfh', 'WFH (ISWERK)')], string="Company", required=True, store=True)
    career_level = fields.Selection([('rank_and_file', 'Rank and File'), ('managerial', 'Managerial'), 
                                     ('executive', 'Executive')], string="Career Level", store=True)
    audio_clip_needed = fields.Boolean('Audio Clip Needed', store=True)
    assessment_needed = fields.Boolean('Assessment Needed', store=True)
    calibration_needed = fields.Boolean('Calibration Needed', store=True)
    priority = fields.Selection([('no', 'No'), ('yes', 'Yes')], string="Priority", store=True)
    calibration_call_availability = fields.Datetime(string='Calibration Availability for Calibration Call', store=True)
    calibration_date = fields.Date(string='Calibration Date', store=True)
    start_date = fields.Date(string='Target Start Date', store=True)
    client_classification = fields.Selection([('new', 'New'), ('existing', 'Existing'), 
                                              ('sales', 'Sales'), ('support_hiring', 'Support Hiring')], string="Client Classification", store=True)
    job_classification = fields.Selection([('generic', 'Generic'), ('tech', 'Tech'), 
                                           ('niche', 'Niche'), ('executive', 'Executive')], string="Job Classification", required=True, store=True)
    support_team = fields.Char(string='Support Team', store=True)
    position_classification = fields.Selection([('growth', 'Growth'), ('new', 'New'), 
                                           ('backfill', 'Backfill'), ('support_hiring', 'Support Hiring')], string="Position Classification", store=True)
    industry = fields.Selection(
        [('back office', 'Back Office'), ('customer service', 'Customer Service'), ('digital', 'Digital'),
         ('finance', 'Finance'), ('medical', 'Medical'), ('operations support', 'Operations Support'),
         ('sales', 'Sales'), ('supply chain', 'Supply Chain'), ('tech', 'Tech')], related="job_id.industry", 
        string='Industry', store=True)
    # industry = fields.Selection(
    #     [('back office', 'Back Office'), ('customer service', 'Customer Service'), ('digital', 'Digital'),
    #      ('finance', 'Finance'), ('medical', 'Medical'), ('operations support', 'Operations Support'),
    #      ('sales', 'Sales'), ('supply chain', 'Supply Chain'), ('tech', 'Tech')], string='Industry', store=True)
    salary_package = fields.Char(string='Salary Package', store=True)
    client_website = fields.Char(string='Client Website', store=True)
    
    # Requisition SLA and Status Fields
    requisition_status = fields.Selection(
        [('for_calibration', 'For Calibration'),
         ('for_pooling', 'For Pooling'),
         ('open', 'Open'),
         ('reopen', 'Reopened'),
         ('ongoing_sourcing', 'Ongoing Sourcing'),
         ('on_hold', 'On Hold'),
         ('cancelled', 'Cancelled'),
         ('recalibrate', 'Recalibrate'),
         ('filled', 'Filled'),
         ('completed', 'Completed')],
        string='Requisition Status', default='for_calibration', store=True)
    date_cancelled = fields.Datetime(string='Date Cancelled', compute='_compute_requisition_status', store=True)
    # date_cancelled = fields.Datetime(string='Date Cancelled', store=True)
    date_onhold = fields.Datetime(string='Date Onhold', compute='_compute_requisition_status', store=True)
    # date_onhold = fields.Datetime(string='Date Onhold', store=True)
    date_filled = fields.Datetime(string='Date Filled', compute='_compute_requisition_status', store=True)
    # date_filled = fields.Datetime(string='Date Filled', store=True)
    date_completed = fields.Datetime(string='Date Completed', compute='_compute_requisition_status', store=True)
    # date_completed = fields.Datetime(string='Date Completed', store=True)
    date_reopen = fields.Datetime(string='Date Reopen', compute='_compute_requisition_status', store=True)
    # date_reopen = fields.Datetime(string='Date Reopen', store=True)
    cancelled_reason = fields.Selection([('pro_active', 'Pro-Active'), ('abandoned', 'Abandoned')], string='Cancelled Reason', store=True)
    date_opened = fields.Char(string='Date Opened', compute="_compute_date_opened", store=True)
    onhold_cancelled_remarks = fields.Text(string='Onhold/Cancelled Remarks', store=True)
    requisition_url = fields.Text(string='Requisition Url', compute="_compute_url", store=True)
    # requisition_url = fields.Text(string='Requisition Url', store=True)
    sla_met = fields.Selection([('no', 'No'), ('yes', 'Yes')], string='SLA Met?', compute="_compute_sla_met", store=True)
    days_to_fill = fields.Integer(string='Days to Fill', compute="_compute_days_to_fill", store=True)
    days_passed = fields.Selection(
        [('less_than_30_days', 'Less than 30 days'), ('passed_30_days', 'Passed 30 days')], string='Days Passed', compute="_compute_days_passed", store=True)
    
        # SLA Fields
    sourcing_date = fields.Datetime(string='Sourcing Date', store=True)
    req_ageing = fields.Integer(string='Number of Days Passed', compute='_compute_requisition_sla')
    # req_ageing = fields.Integer(string='Number of Days Passed')
    req_ageing_total = fields.Integer(string='Number of Days Passed')
    days_onhold = fields.Integer(string='Total Days Onhold', store=True)
    hold_start_date = fields.Datetime(string='Onhold Start Date', store=True)
    hold_end_date = fields.Datetime(string='Onhold End Date', store=True)
    old_onhold_checker = fields.Integer(string='Old Onhold Checker', store=True)
    onhold_counter = fields.Integer(string='Onhold Counter')
    end_date = fields.Datetime(string='End Date', store=True)
    datetime_today = fields.Datetime(string='Datetime Today', compute='_compute_datetime_today')
    # datetime_today = fields.Datetime(string='Datetime Today')
    
    # Staffing Overview Fields
    headcount_demand = fields.Integer(string='Headcount Demand', store=True)
    remaining_vacancy = fields.Integer(string='Remaining Vacancy', compute="_compute_remaining_vacancy", store=True)
    filled = fields.Integer(string='Filled', store=True)
    projected_headcount = fields.Integer(string='Projected Headcount to Close', store=True)
    projected_neo_date = fields.Date(string='Projected NEO Date', store=True)
    
    # Recruitment and Client POC Fields
    requestor_id = fields.Many2one('hr.recruitment.requestor', string="Requestor", related="job_id.requestor_id", store=True)
    # requestor_id = fields.Many2one('hr.recruitment.requestor', string="Requestor", store=True)
    hiring_manager = fields.Char(string='Hiring Manager', store=True)
    hiring_manager_email = fields.Char(string='Hiring Manager Email Address', store=True)
    sec_hiring_manager = fields.Char(string='Secondary Hiring Manager POC', store=True)
    recruitment_manager_id = fields.Many2one('hr.recruitment.manager', string="Recruitment Manager", store=True)
    assigned_recruiter_id = fields.Many2one('hr.recruitment.recruiter', string="Assigned Recruiter", store=True)
    
    # Requisition Remarks
    requisition_remarks = fields.Text(string='Requisition Remarks', store=True)
    
    # Other Fields
    other_remarks = fields.Text(string="Other Remarks", store=True)
    
    # Applicants
    applicant_ids = fields.One2many('hr.applicant', 'requisition_ref_id', string="Applicants", store=True)
    
    # Getting applicant records function
    def compute_hired_applicants(self):
        for requisition in self:
            requisition.applicant_ids = self.env['hr.applicant'].search([('requisition_identifier_id', '=', requisition.id),'|', ('stage_id', '=', 'Signed: Job Offer'), ('jo_status', '=', 'accepted')])
    
    def compute_all_applicants(self):
        for requisition in self:
            requisition.applicant_ids = self.env['hr.applicant'].search([('requisition_identifier_id.req_id', '=', requisition.req_id)])
    
    # Days Passed Computation
    @api.depends('req_ageing_total')
    def _compute_days_passed(self):
        for rec in self:
            if rec.req_ageing < 31:
                self.days_passed = 'less_than_30_days'
            elif rec.req_ageing > 30:
                self.days_passed = 'passed_30_days'
    
    # SLA Met Automation
    @api.depends('date_filled')
    def _compute_sla_met(self):
        for record in self:
            if record.requisition_status == 'filled' or record.requisition_status == 'closed':
                if record.job_classification == 'generic':
                    if record.days_to_fill <= 30:
                        record.sla_met = 'yes'
                    else:
                        record.sla_met = 'no'    
                if record.job_classification == 'niche':
                    if record.days_to_fill <= 45:
                        record.sla_met = 'yes'
                    else:
                        record.sla_met = 'no'        
                if record.job_classification == 'tech':
                    if record.days_to_fill <= 60:
                        record.sla_met = 'yes'
                    else:
                        record.sla_met = 'no'        
                if record.job_classification == 'executive':
                    if record.days_to_fill <= 90:
                        record.sla_met = 'yes'
                    else:
                        record.sla_met = 'no'

    # Days to fill automation
    @api.depends('requisition_status')
    def _compute_days_to_fill(self):
        for record in self:
            if not record.days_to_fill:
                if record.requisition_status == 'filled' or record.requisition_status == 'completed':
                    record.days_to_fill = record.req_ageing
                
    # Set to priority function
    def priority_records_requisition(self):
        for record in self:
            record.write({'priority': 'yes'})
    
    # Set to unpriority function
    def unpriority_records_requisition(self):
        for record in self:
            record.write({'priority': 'no'})
    
    # Remaining Vacancy Auto-Compute
    @api.depends('headcount_demand', 'filled')
    def _compute_remaining_vacancy(self):
        for record in self:
            if not record.headcount_demand:
                record.remaining_vacancy = False
            else:
                record.remaining_vacancy = self.headcount_demand
                record.remaining_vacancy = self.headcount_demand - record.filled
    
    # Auto removal of Job Title on Client Name change
    @api.depends('department_id')
    def _compute_job_id(self):
        for record in self:
            record.job_id = False
    
    # Auto generation of Requisition URL
    @api.depends('req_id')        
    def _compute_url(self):
        base_url = 'http://10.2.1.200:8070/odoo/action-274'
        for record in self:
            record.requisition_url = f"{base_url}/{record.id}" if record.id else ''
    
    
    # Requisition Status Date Automation
    @api.depends('requisition_status')
    def _compute_requisition_status(self):
        for record in self:
            if record.requisition_status == 'cancelled':
                record.date_cancelled = record.datetime_today
            if record.requisition_status == 'on_hold':
                record.date_onhold = record.datetime_today
            if record.requisition_status == 'filled':
                record.date_filled = record.datetime_today
            if record.requisition_status == 'completed':
                record.date_completed = record.datetime_today
            if record.requisition_status == 'reopen':
                record.date_reopen = record.datetime_today
                
    # Date Opened Automation
    @api.depends('requisition_status')
    def _compute_date_opened(self):
        for rec in self:
            user_timezone = pytz.timezone('Asia/Singapore')
            # Get the current date and time in the user's time zone
            user_time = datetime.now(user_timezone)
            formatted_date = user_time.strftime('%m/%d/%Y %H:%M:%S')
            if rec.requisition_status == 'for_calibration':
                rec.date_opened = formatted_date
    
    # Current date and time automatic counting
    @api.depends('datetime_today')
    def _compute_datetime_today(self):
        self.datetime_today = datetime.today()
    
    # SLA computation
    def _compute_requisition_sla(self):
        for rec in self:
            date_today = datetime.today()
            date_today = pd.to_datetime(date_today.astimezone(pytz.timezone('Asia/Manila')), format="%Y-%m-%d").date()
            
            if rec.sourcing_date:
                date_create = pd.to_datetime(rec.sourcing_date.astimezone(pytz.timezone('Asia/Manila')),
                                           format="%Y-%m-%d").date()
                days = np.busday_count(date_create, date_today)
                if date_create.weekday() == 5 or date_create.weekday() == 6:
                    rec.req_ageing = days + 2
                else:
                    if date_today.weekday() == 5 or date_today.weekday() == 6:
                        rec.req_ageing = days
                    else:
                        rec.req_ageing = days + 1
            
                if rec.requisition_status == 'recalibrate':
                    rec.req_ageing = False
                    rec.req_ageing_total = False
                    rec.days_onhold = False
                    rec.hold_start_date = False
                    rec.hold_end_date = False
                    rec.old_onhold_checker = False
                    rec.onhold_counter = False
                    rec.sourcing_date = False
                    rec.date_onhold = False
                    rec.end_date = False
                    rec.date_filled = False
                    rec.date_cancelled = False

                # ONHOLD CODE

                if rec.requisition_status == 'on_hold' and rec.date_onhold:

                    # start date and end date has date and the onhold days has old value
                    if rec.date_onhold != False and rec.hold_end_date != False and rec.days_onhold > 0:
                        # END DATE HERE IS THE DATE REMOVED FROM BEING ON HOLD
                        rec.end_date = date_today 
                        var_onhold_start_date = rec.date_onhold
                        var_onhold_start_date = pd.to_datetime(var_onhold_start_date.astimezone(pytz.timezone('Asia/Manila')), format="%Y-%m-%d").date()
                        # var_onhold_end_date = rec.x_onhold_end_date
                        var_onhold_end_date = datetime.today()
                        var_onhold_end_date = pd.to_datetime(var_onhold_end_date.astimezone(pytz.timezone('Asia/Manila')),
                                                            format="%Y-%m-%d").date()
                        # since end date has value the value of end date is rec.x_onhold_end_date
                        var_onhold_days = np.busday_count(var_onhold_start_date, var_onhold_end_date)

                        # rec.x_onhold_end_date = ''

                        if rec.old_onhold_checker == 0:
                            rec.old_onhold_checker = 1
                            # rec.x_req_recruitment_hiring_manager = 'new'

                            if var_onhold_start_date.weekday() == 5 or var_onhold_start_date.weekday() == 6:
                                rec.days_onhold = var_onhold_days + 1
                            else:
                                if var_onhold_end_date.weekday() == 5 or var_onhold_end_date.weekday() == 6:
                                    rec.days_onhold = rec.days_onhold + var_onhold_days
                                else:
                                    rec.days_onhold = (rec.days_onhold + var_onhold_days)
                            rec.onhold_counter = rec.onhold_counter + 1
                        else:
                            rec.old_onhold_checker = 2
                            # rec.x_req_recruitment_hiring_manager = 'old'

                        # rec.x_req_sla = rec.x_req_sla - rec.x_onhold_days
                        # rec.x_req_sla = rec.x_req_sla

                    # start date has value and end date is null and the onhold days is 0
                    else:
                        # rec.x_onhold_start_date = rec.x_date_today
                        var_onhold_start_date = rec.date_onhold
                        var_onhold_start_date = pd.to_datetime(var_onhold_start_date.astimezone(pytz.timezone('Asia/Manila')), format="%Y-%m-%d").date()
                        # var_onhold_end_date = datetime.today()
                        var_onhold_end_date = datetime.today()
                        var_onhold_end_date = pd.to_datetime(var_onhold_end_date.astimezone(pytz.timezone('Asia/Manila')),
                                                            format="%Y-%m-%d").date()
                        # since end date is null the value of end date is current datetime today
                        var_onhold_days = np.busday_count(var_onhold_start_date, var_onhold_end_date)

                        if var_onhold_start_date.weekday() == 5 or var_onhold_start_date.weekday() == 6:
                            rec.days_onhold = var_onhold_days + 1
                        else:
                            if var_onhold_end_date.weekday() == 5 or var_onhold_end_date.weekday() == 6:
                                rec.days_onhold = var_onhold_days
                            else:
                                rec.days_onhold = var_onhold_days
                        # rec.x_req_sla = rec.x_req_sla - rec.x_onhold_days
                        rec.old_onhold_checker = 1
                        rec.onhold_counter = rec.onhold_counter + 1

                # elif rec.x_requisition_status == 'in progress' and rec.x_onhold_days > 0:
                #     rec.x_req_sla = rec.x_req_sla - rec.x_onhold_days
                #     rec.x_old_onhold_checker = 0

                elif rec.requisition_status == 'pending' and rec.days_onhold < 1 and rec.req_ageing <= 1:
                    rec.req_ageing = 0

                elif rec.requisition_status == 'cancelled' and rec.date_onhold:
                    # rec.x_onhold_start_date = rec.x_date_today
                    var_onhold_start_date = rec.date_cancelled
                    var_onhold_start_date = pd.to_datetime(var_onhold_start_date.astimezone(pytz.timezone('Asia/Manila')),
                                                        format="%Y-%m-%d").date()
                    var_onhold_end_date = datetime.today()
                    var_onhold_end_date = pd.to_datetime(var_onhold_end_date.astimezone(pytz.timezone('Asia/Manila')),
                                                        format="%Y-%m-%d").date()
                    # since end date is null the value of end date is current datetime today
                    var_onhold_days = np.busday_count(var_onhold_start_date, var_onhold_end_date)

                    if var_onhold_start_date.weekday() == 5 or var_onhold_start_date.weekday() == 6:
                        rec.days_onhold = var_onhold_days + 1
                    else:
                        if var_onhold_end_date.weekday() == 5 or var_onhold_end_date.weekday() == 6:
                            rec.days_onhold = var_onhold_days
                        else:
                            rec.days_onhold = var_onhold_days

                    rec.req_ageing = rec.req_ageing
                    rec.old_onhold_checker = 0

                elif rec.requisition_status == 'closed':
                    rec.days_to_fill = rec.req_ageing
                    var_onhold_start_date = rec.date_completed
                    var_onhold_start_date = pd.to_datetime(var_onhold_start_date.astimezone(pytz.timezone('Asia/Manila')),
                                                        format="%Y-%m-%d").date()
                    var_onhold_end_date = datetime.today()
                    var_onhold_end_date = pd.to_datetime(var_onhold_end_date.astimezone(pytz.timezone('Asia/Manila')),
                                                        format="%Y-%m-%d").date()
                    # since end date is null the value of end date is current datetime today
                    var_onhold_days = np.busday_count(var_onhold_start_date, var_onhold_end_date)

                    if var_onhold_start_date.weekday() == 5 or var_onhold_start_date.weekday() == 6:
                        rec.days_onhold = var_onhold_days + 1
                    else:
                        if var_onhold_end_date.weekday() == 5 or var_onhold_end_date.weekday() == 6:
                            rec.days_onhold = var_onhold_days
                        else:
                            rec.days_onhold = var_onhold_days

                    rec.req_ageing = rec.req_ageing
                    rec.old_onhold_checker = 0

                if rec.req_ageing < 0:
                    rec.req_ageing = 0

            rec.req_ageing_total = rec.req_ageing - rec.days_onhold
            rec.req_ageing = rec.req_ageing_total     