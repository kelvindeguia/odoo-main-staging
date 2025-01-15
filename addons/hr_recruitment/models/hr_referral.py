# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import fields, models
from odoo.exceptions import ValidationError
import pytz

class Referral(models.Model):
    _name = "hr.referral"
    _description = "Referral"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = "name"

    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    name = fields.Char(string="Candidate Name", store=True, index=True)
    mobile_number = fields.Char(string="Candidate Mobile Number", store=True, index=True)
    email = fields.Char(string="Candidate Email Address", store=True, index=True)
    emp_name = fields.Char(string="Employee Name", store=True, index=True)
    emp_account = fields.Char(string="Employee Account/Program/Department", store=True, index=True)
    emp_id = fields.Char(string="Employee ID", store=True, index=True)
    employee_email = fields.Char(string='Employee Email', store=True, index=True)
    referral_ids = fields.Many2many(comodel_name='ir.attachment',
                                    relation='m2m_ir_referral_rel',
                                    column1='m2m_id',
                                    column2='attachment_id',
                                    string='Resume')
    desired_position = fields.Char(string="Referral's Desired Position", index=True)
    user_id = fields.Many2one('res.users', string='User')
    status = fields.Selection([('untapped', 'Untapped'), ('dispatched', 'Dispatched')], string='Status', default='untapped', store=True)
    dispatch_date = fields.Datetime(string='Dispatch Date')
    # record_ageing = fields.Integer(string='Record Ageing', compute="_compute_record_ageing")
    record_ageing = fields.Integer(string='Record Ageing')
    record_ageing_ref = fields.Integer(string='Record Ageing Reference', store=True)
    # date_today = fields.Datetime(string='Datetime Today', compute="_compute_date_today")
    date_today = fields.Datetime(string='Datetime Today')
    update_logs = fields.Text(string='Update Logs', store=True, default="")
    requisition_id = fields.Many2one('hr.requisition', string='Requisition ID', store=True)
    # received_date = fields.Char('Received Date', store=True, compute="_compute_received_date")
    received_date = fields.Char(string='Received Date', store=True)
    dispatch_date_ref = fields.Char(string='Received Date', store=True)
    job_id = fields.Many2one('hr.job', string='Job Position', store=True)
    department_id = fields.Many2one('hr.department', string='Department Name', store=True)
    
    # Transfer to all applicants function
    def transfer_records_applicants(self):
        for record in self:
            if not record.requisition_id:
                raise ValidationError(
                    f"'{self.name}' | Please input a Requisition ID before transferring the referral.")

            record.sudo().write({'status': 'dispatched'})
            record.write({'dispatch_date': record.date_today})

            # set timezone
            user_timezone = 'Asia/Singapore'
            utc_now = datetime.utcnow()
            # convert time
            user_timezone = pytz.timezone(user_timezone)
            user_time = utc_now.astimezone(user_timezone)

            if not self.update_logs:
                self.update_logs = ""
            self.update_logs += f"{self.env.user.name}\n{user_time:%m/%d/%Y %I:%M%p} | Status: {self.status}\n\n"

            # Create a list to store attachment IDs for the transferred records
            attachment_ids = []

            for attachment in record.referral_ids:
                new_attachment = attachment.copy()
                attachment_ids.append(new_attachment.id)

            # Create a new hr.applicant record with the attachments transferred to the new referral_ids field
            new_applicant = self.env['hr.applicant'].create({
                'partner_name': record.name,
                'mobile_number': record.mobile_number,
                'email_from': record.email,
                'employee_email': record.employee_email,
                'employee_id': record.emp_id,
                'employee_account': record.emp_account,
                'channel_id': 4,
                'specific_source_id': 68,
                'referral_position': record.desired_position,
                'referrer_name': record.emp_name,
                'requisition_id': record.requisition_id.id,
                'resume_ids': [(6, 0, attachment_ids)]  # Set the copied attachments to the new referral_ids field
            })
        return True