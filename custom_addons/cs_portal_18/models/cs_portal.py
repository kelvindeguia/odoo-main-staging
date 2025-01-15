import logging
import pytz
import threading
import pandas as pd
import numpy as np
import re
import logging
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
from psycopg2 import sql

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.iap.tools import iap_tools
from odoo.addons.mail.tools import mail_validation
from odoo.addons.phone_validation.tools import phone_validation
from odoo.exceptions import UserError, AccessError
from odoo.osv import expression
from odoo.tools.translate import _ 
from odoo.tools import date_utils
from odoo.tools.misc import get_lang
from random import randint
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class CSPortal(models.Model):
    _name = 'cs.portal.main'
    _description = 'CS Portal Main'
    _rec_name = 'account_name'
    _inherit = ['mail.thread.cc',
               'mail.thread.main.attachment',
               'mail.activity.mixin',
               'utm.mixin']
    
    active = fields.Boolean(default=True)
    account_name = fields.Char('Account Name', store=True, required=True)
    account_status = fields.Selection([('active', 'Active'),
                                       ('inactive', 'Inactive'),
                                       ('sourcing', 'Sourcing')], 'Account Status', store=True)
    ceo = fields.Char('CEO', store=True)
    website = fields.Char('Website', store=True)
    year_founded = fields.Char('Year Founded', store=True)
    contract_start_date = fields.Date('Contract Start Date', store=True)
    industry = fields.Char('Industry', store=True)
    
    country_id = fields.Many2one('res.country', string="Country", store=True)
    state_id = fields.Many2one('res.country.state', string="State", domain="[('country_id', '=', country_id)]", store=True)
    city = fields.Char(string="City", store=True) 
    street = fields.Char(string="Street", store=True)
    street_number = fields.Char('Street Number', store=True)
    zip_code = fields.Char('Zip Code', store=True)
    
    address = fields.Char('Address', store=True)
    contact_phone_number = fields.Char('Contact (Phone)', store=True)
    telephone_number = fields.Char('Contact (Telephone)', store=True)
    contact_email = fields.Char('Contact (Email)', store=True)
    company_headcount = fields.Integer('Company Headcount', store=True)
    street_name = fields.Char('Street Name', store=True)
    city = fields.Char('City', store=True)
    state = fields.Char('State', store=True)
    
    kanban_state = fields.Selection([
        ('on_hold', 'Amber'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='done', required=True)
    
    #EDIT BUTTONS FOR CLIENTS SECTIONS
    edit = fields.Boolean('Edit Company Profile', default=True, store=True, required=True)
    edit_poc = fields.Boolean('Edit POC', default=True, store=True, required=True)
    edit_client_interactions = fields.Boolean('Edit Client Interactions', default=True, store=True, required=True)
    edit_business_reviews = fields.Boolean('Edit Business Reviews', default=True, store=True, required=True)
    edit_attrition = fields.Boolean('Edit Attrition', default=True, store=True, required=True)
    edit_requisition = fields.Boolean('Edit Requisition', default=True, store=True, required=True)
    edit_revenue_generation = fields.Boolean('Edit Revenue Generation', default=True, store=True, required=True)
    edit_attachments = fields.Boolean('Edit Attachments', default=True, store=True, required=True)

    # edit_button = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Edit Button', default='yes', store=True)

    #Many2one fields#
    account_owner_id = fields.Many2one('cs.portal.account.owner', string='Account Owner', index=True)
    secondary_owner_id = fields.Many2one('cs.portal.secondary.owner', string='Secondary Owner', index=True)
    contract_length_id = fields.Many2one('cs.portal.contract.length', string='Contract Length')
    separation_status_id = fields.Many2one('cs.portal.separation.status', string='Separation Status', store=True)
    reason_for_separation_id = fields.Many2one('cs.portal.reason.for.separation', string='REASON For Separation (Resignation Letter/ Termination notice)', store=True)
    type_of_revenue_generation_id = fields.Many2one('cs.portal.revenue.generation.type', string='Revenue Generation Type', store=True)
    # type_of_interactions_id = fields.Many2one('cs.portal.revenue.generation.type', string='Revenue Generation Type', store=True)
    
    #EDIT AND SAVE FUNCTIONALITY
    # Trigger for Company Profile
    def compute_edit_information(self):
        for record in self:
            record.edit = False

    def compute_save_information(self):
        for record in self:
            record.edit = True  

    #POCs
    def compute_edit_poc(self):
        for record in self:
            record.edit_poc = False
    def compute_save_poc(self):
        for record in self:
            record.edit_poc = True

    #Client Interactions
    def compute_edit_client_interactions(self):
        for record in self:
            record.edit_client_interactions = False
    def compute_save_client_interactions(self):
        for record in self:
            record.edit_client_interactions = True
    
    #Business Reviews
    def compute_edit_business_reviews(self):
        for record in self:
            record.edit_business_reviews = False
    def compute_save_business_reviews(self):
        for record in self:
            record.edit_business_reviews = True
    
    #Attrition
    def compute_edit_attrition(self):
        for record in self:
            record.edit_attrition = False
    def compute_save_attrition(self):
        for record in self:
            record.edit_attrition = True
    
     #Requisition
    def compute_edit_requisition(self):
        for record in self:
            record.edit_requisition = False
    def compute_save_requisition(self):
        for record in self:
            record.edit_requisition = True

     #Revenue Generation
    def compute_edit_revenue_generation(self):
        for record in self:
            record.edit_revenue_generation = False
    def compute_save_revenue_generation(self):
        for record in self:
            record.edit_revenue_generation = True

     #Attachments
    def compute_edit_attachments(self):
        for record in self:
            record.edit_attachments = False
    def compute_save_attachments(self):
        for record in self:
            record.edit_attachments = True
    
    # US FORMAT PHONE NUMBER
    @api.constrains('contact_phone_number')
    def _check_contact_phone_number_format(self):
        us_phone_pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
        for record in self:
            if record.contact_phone_number and not us_phone_pattern.match(record.contact_phone_number):
                raise ValidationError("Phone number must be in the format XXX-XXX-XXXX.")

    # Validation for correct email format
    @api.constrains('contact_email')
    def _check_contact_email_format(self):
        contact_email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        for record in self:
            if record.contact_email and not re.match(contact_email_regex, record.contact_email):
                raise ValidationError(f"Invalid email format: {record.contact_email}. Please provide a valid email address.")

    
    #Many2many fields#
    tag_ids = fields.Many2many('cs.portal.tag', string='Tags')
    attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                           relation='m2m_ir_attachment_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Attachments')
    jd_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                           relation='jd_ir_attachment_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Job Descriptions Attachments',
                                           domain="[('res_model', '=', 'cs.portal.main'), ('res_id', '=', id)]")
    mom_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                           relation='mom_ir_attachment_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Minutes of the Meeting Attachments',
                                           domain="[('res_model', '=', 'cs.portal.main'), ('res_id', '=', id)]")
    cn_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                           relation='cn_ir_attachment_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Calibration Notes Attachments',
                                           domain="[('res_model', '=', 'cs.portal.main'), ('res_id', '=', id)]")
    cv_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                           relation='cv_ir_attachment_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Client Validation Attachments',
                                           domain="[('res_model', '=', 'cs.portal.main'), ('res_id', '=', id)]")
    attachments = fields.Binary(string='Attachments', attachment=True, store=True)
    type_of_revenue_generation_ids = fields.Many2many('cs.portal.revenue.generation.type', string='Revenue Generation Types', store=True)
    interactions_owner_ids = fields.Many2many('cs.portal.interactions.owner', string='Owner')
    filtered_revenue_generation_ids = fields.Many2many('cs.portal.revenue.generation', compute='_compute_filtered_revenue_generation_ids', string='Filtered Revenue Generations', store=False)
    revenue_generation_ids = fields.Many2many('cs.portal.revenue.generation', store=True, string='Revenue Generation')
    
    # @api.depends('type_of_revenue_generation_id')
    # def _compute_filtered_revenue_generation_ids(self):
    #     for record in self:
    #         if record.type_of_revenue_generation_id:
    #             filtered_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('type_of_revenue_generation_id', '=', record.type_of_revenue_generation_id.id),
    #                 ('record_relation', '=', record.record_id)
    #             ])
    #         else:
    #             filtered_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('record_relation', '=', record.record_id)
    #             ])
    #         record.filtered_revenue_generation_ids = filtered_revenues
    
    #Related Fields#
    poc_information_ids = fields.One2many('cs.portal.poc.information', 'cs_portal_main_id', string='Point of Contact Information')
    client_interactions_ids = fields.One2many('cs.portal.client.interactions', 'cs_portal_main_id', string='Client Interactions')
    business_reviews_ids = fields.One2many('cs.portal.business.reviews', 'cs_portal_main_id', string='Business Reviews')
    attrition_ids = fields.One2many('cs.portal.attrition', 'cs_portal_main_id', string='Attrition')
    requisitions_ids = fields.One2many('cs.portal.requisition', 'cs_portal_main_id', string='Requisitions')
    hr_requisitions_ids = fields.One2many('hr.requisition', 'cs_portal_main_id', string='Requisitions')
    # revenue_generation_ids = fields.One2many('cs.portal.revenue.generation', 'cs_portal_main_id', compute="_compute_type_of_revenue_generation_id", store=True, readonly=False, string='Revenue Generation')
    revenue_generation_ids = fields.One2many('cs.portal.revenue.generation', 'cs_portal_main_id', compute="_compute_type_of_revenue_generation_id", store=True, readonly=False, string='Revenue Generation')
    revenue_generation_idss = fields.Many2many('cs.portal.revenue.generation', 'cs_portal_main_id', compute="_compute_type_of_revenue_generation_id", store=True, string='Revenue Generation')
    revenue_ids = fields.One2many('cs.portal.revenue.generation', 'cs_main_ref_id', compute="_compute_revenue_ids", store=True)
    
    @api.depends('type_of_revenue_generation_id')
    def _compute_revenue_ids(self):
        for revenue in self:
            revenue.revenue_ids = self.env['cs.portal.revenue.generation'].search([('cs_main_identifier_id', '=', revenue.id), ('type_of_revenue_generation_id', '=', revenue.type_of_revenue_generation_id.id)])
    
    record_id = fields.Integer(string='Record ID', store=True)
    # revenue_generation_ids = fields.One2many('cs.portal.revenue.generation', 'cs_portal_main_id', readonly=False, string='Revenue Generation')
    
    @api.depends('type_of_revenue_generation_id')
    def _compute_type_of_revenue_generation_id(self):
        for record in self:
            if record.type_of_revenue_generation_id:
                filtered_revenues = self.env['cs.portal.revenue.generation'].search([
                    ('type_of_revenue_generation_id', '=', record.type_of_revenue_generation_id.id),
                    ('record_relation', '=', record.record_id)
                ])
                # Log to check the filtered IDs
                _logger.info('Filtered revenue IDs for type %s and record %s: %s',
                            record.type_of_revenue_generation_id.id, record.record_id, filtered_revenues.ids)
            else:
                filtered_revenues = self.env['cs.portal.revenue.generation'].search([
                    ('record_relation', '=', record.record_id)
                ])
                _logger.info('Default filtered revenue IDs for record %s: %s', 
                            record.record_id, filtered_revenues.ids)
            
            # Update the Many2many relation directly with the filtered IDs
            record.revenue_generation_idss = [(6, 0, filtered_revenues.ids)]

    # @api.depends('type_of_revenue_generation_id')
    # def _compute_type_of_revenue_generation_id(self):
    #     for record in self:
    #         if record.type_of_revenue_generation_id:
    #             # Strictly filter records matching the type and relation
    #             filtered_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('type_of_revenue_generation_id', '=', record.type_of_revenue_generation_id.id),
    #                 ('record_relation', '=', record.record_id)
    #             ])
    #         else:
    #             # Default to all records linked to the main record
    #             filtered_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('record_relation', '=', record.record_id)
    #             ])
            
    #         # Get existing revenue generation records
    #         existing_revenue_ids = record.revenue_generation_ids.ids
            
    #         # Compute new revenue ids to add or keep
    #         new_revenue_ids = set(filtered_revenues.ids)
    #         to_keep_ids = set(existing_revenue_ids) & new_revenue_ids
    #         to_add_ids = new_revenue_ids - to_keep_ids
            
    #         # Update the Many2many relation with only new additions
    #         if to_add_ids:
    #             record.revenue_generation_ids = [(4, id) for id in to_add_ids]

    # @api.depends('type_of_revenue_generation_id')
    # def _compute_type_of_revenue_generation_id(self):
    #     for record in self:
    #         if record.type_of_revenue_generation_id:
    #             # Strictly filter records matching the type and relation
    #             filtered_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('type_of_revenue_generation_id', '=', record.type_of_revenue_generation_id.id),
    #                 ('record_relation', '=', record.record_id)
    #             ])
    #             record.revenue_generation_ids = [(6, 0, filtered_revenues.ids)]
    #         else:
    #             # Default to all records linked to the main record
    #             default_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('record_relation', '=', record.record_id)
    #             ])
    #             record.revenue_generation_ids = [(6, 0, default_revenues.ids)]
    
    # @api.depends('type_of_revenue_generation_id')
    # def _compute_type_of_revenue_generation_id(self):
    #     for record in self:
    #         if record.type_of_revenue_generation_id:
    #             # Search for records matching the type and update the One2many relationship
    #             revenue_records = self.env['cs.portal.revenue.generation'].search([
    #                 ('type_of_revenue_generation_id', '=', record.type_of_revenue_generation_id.id), ('record_relation', '=', record.record_id)
    #             ])
    #             record.revenue_generation_ids = [(6, 0, revenue_records.ids)]
    #         else:
    #             # If no type is set, default to records linked to the current main record
    #             default_revenues = self.env['cs.portal.revenue.generation'].search([
    #                 ('record_relation', '=', record.record_id)
    #             ])
    #             record.revenue_generation_ids = [(6, 0, default_revenues.ids)]
    
    # @api.depends('type_of_revenue_generation_id')
    # def _compute_type_of_revenue_generation_id(self):
    #     for record in self:
    #         if record.type_of_revenue_generation_id:
    #             record.revenue_generation_ids = self.env['cs.portal.revenue.generation'].search([('type_of_revenue_generation_id.id', '=', record.type_of_revenue_generation_id.id), ('cs_portal_main_id', '=', record.record_id)])
    #         if not self.type_of_revenue_generation_id: 
    #             self.revenue_generation_ids = [(6, 0, self.env['cs.portal.revenue.generation'].search([('cs_portal_main_id', '=', record.id)]).ids)]

    class CSPortal_Account_Owner(models.Model):
        _name = 'cs.portal.account.owner'
        _description = 'Account Owner'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Account Owner', store=True, required=True)
        account_owner_ids = fields.Many2one('res.users', string='Account Owner Reference', store=True)
        user_id = fields.Integer('User ID Reference', store=True, related='account_owner_ids.id')
        active_account_owner = fields.Boolean('Account Owner Status', store=True)
        email_address = fields.Char('Email Address', store=True, related='account_owner_ids.login')

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Account Owner already exists!'),
        ]

    class CSPortal_Secondary_Owner(models.Model):
        _name = 'cs.portal.secondary.owner'
        _description = 'Secondary Owner'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Secondary Owner', store=True, required=True)
        account_owner_ids = fields.Many2one('res.users', string='Account Owner Reference', store=True)
        user_id = fields.Integer('User ID Reference', store=True, related='account_owner_ids.id')
        active_secondary_owner = fields.Boolean('Secondary Owner Status', store=True)
        email_address = fields.Char('Email Address', store=True, related='account_owner_ids.login')

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Secondary Owner already exists!'),
        ]

    class CSPortal_Contract_Length(models.Model):
        _name = 'cs.portal.contract.length'
        _description = 'Contract Length'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Contract Length', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Contract Length already exists!'),
        ]

    class CSPortal_Tag(models.Model):
        _name = 'cs.portal.tag'
        _description = 'CS Portal Tag'
        _rec_name = 'name'

        def _get_default_color(self):
            return randint(1, 11)

        active = fields.Boolean(default=True)
        name = fields.Char('Tag Name', required=True, translate=True)
        color = fields.Integer('Color', default=_get_default_color)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Tag name already exists!'),
        ]

    class CSPortal_POC_Information(models.Model):
        _name = 'cs.portal.poc.information'
        _description = 'CS Portal POC Information'
        _rec_name = 'name'

        active = fields.Boolean(default=True)

        cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
        hierarchy = fields.Selection([('primary', 'Primary'), ('secondary', 'Secondary'), ('tertiary', 'Tertiary'), ], 'Hierarchy', store=True)
        health = fields.Selection([('red', 'Red'), ('orange', 'Orange'), ('green', 'Green'), ], 'Health', store=True)
        kanban_state = fields.Selection([
        ('on_hold', 'Amber'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Health')
        name = fields.Char('Name', store=True, required=True)
        department = fields.Char('Department', store=True)
        designation = fields.Char('Designation', store=True)
        email = fields.Char('Email', store=True)
        phone = fields.Char('Phone', store=True)
        chat_platform = fields.Char('Chat Platform', store=True)
        chat_platform_ids = fields.Many2many('cs.portal.chat.platform', string='Chat Platform')
        influence_type = fields.Selection([('decision_maker', 'Decision Maker'), ('detractor', 'Dectractor'), ('influencer', 'Influencer'), ('promoter', 'Promoter'), ], 'Influence Type', store=True)

        # US FORMAT PHONE NUMBER
        @api.constrains('phone')
        def _check_phone_format(self):
            us_phone_pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
            for record in self:
                if record.phone and not us_phone_pattern.match(record.phone):
                    raise ValidationError("Phone number must be in the format XXX-XXX-XXXX.")

        # Validation for correct email format
        @api.constrains('email')
        def _check_email_format(self):
            email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            for record in self:
                if record.email and not re.match(email_regex, record.email):
                    raise ValidationError(f"Invalid email format: {record.email}. Please provide a valid email address.")

    class CSPortal_Client_Interactions(models.Model):
        _name = 'cs.portal.client.interactions'
        _description = 'CS Portal Client Interactions'
        _rec_name = 'id'
        _inherit = ['mail.thread.cc',
                'mail.activity.mixin',
                'utm.mixin']

        active = fields.Boolean(default=True)
        cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
        date = fields.Date('Date', store=True)
        type_of_interactions_id = fields.Many2one('cs.portal.client.interactions.type', 'Type', store=True)
        notes = fields.Text('Notes', store=True)
        request = fields.Char('Request', store=True)
        requested_by = fields.Char('Requested By', store=True)
        client_id = fields.Many2one('cs.portal.poc.information', string='Requested By', store=True)
        poc_information_ids = fields.One2many('cs.portal.poc.information', 'cs_portal_main_id', string='Requested By')
        account_owner_id = fields.Many2one('cs.portal.account.owner', string='Owner', index=True)
        interactions_owner_id = fields.Many2one('cs.portal.client.interactions.owner', string='Owner', store=True)
        interactions_owner_ids = fields.Many2many('cs.portal.interactions.owner', string='Owner')

    class CSPortal_Client_Interactions_Type(models.Model):
        _name = 'cs.portal.client.interactions.type'
        _description = 'CS Portal Client Interactions Type of Interactions'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Type of Interactions', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Type of Interactions already exists!'),
        ]
    
    class CSPortal_Client_Interactions_Owner(models.Model):
        _name = 'cs.portal.client.interactions.owner'
        _description = 'CS Portal Client Interactions Owner'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Client Interactions Owner', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Client Interactions Owner already exists!'),
        ]
    
    class CSPortal_Interactions_Owner(models.Model):
        _name = 'cs.portal.interactions.owner'
        _description = 'CS Portal Client Interactions Owner'
        _rec_name = 'name'

        def _get_default_color(self):
            return randint(1, 11)

        active = fields.Boolean(default=True)
        name = fields.Char('Owner', required=True, translate=True)
        color = fields.Integer('Color', default=_get_default_color)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Owner name already exists!'),
        ]

    class CSPortal_Client_Business_Reviews(models.Model):
        _name = 'cs.portal.business.reviews'
        _description = 'CS Portal Business Reviews'
        _rec_name = 'participants'

        active = fields.Boolean(default=True)
        cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
        type_of_business_reviews_id = fields.Many2one('cs.portal.client.meeting.type', 'Meeting Type', store=True)
        participants = fields.Char('Participants', store=True)
        cs_participants = fields.Selection([('isupport_participants', 'iSupport Participants'), ('client_participants', 'Client Participants'), ], 'Participants', store=True)
        pending_items = fields.Char('Pending Items', store=True)
        status = fields.Selection([('new', 'New'), ('pending', 'Pending'), ('completed', 'Completed'), ('reschedule', 'Reschedule'), ('cancelled', 'Cancelled'), ], 'Status', store=True)
        notes = fields.Text('Take Away Items', store=True)

        #For cs_participants functionality trigger
        isupport_participant = fields.Text('iSupport Participants', store=True)
        client_participant = fields.Text('Client Participants', store=True)
    
    class CSPortal_Client_Meeting_Type(models.Model):
        _name = 'cs.portal.client.meeting.type'
        _description = 'CS Portal Client Meeting Type'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Meeting Type', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Type of Meeting already exists!'),
        ]

    class CSPortal_Attrition(models.Model):
        _name = 'cs.portal.attrition'
        _description = 'CS Portal Attrition'
        _rec_name = 'full_name'

        active = fields.Boolean(default=True)
        cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
        employee_id = fields.Char('EID', store=True)
        full_name = fields.Char('Full Name', store=True, required=True)
        position = fields.Char('Position', store=True)
        employment_status = fields.Selection([('regular', 'REGULAR'), ('probationary', 'PROBATIONARY')], 'Employment Status', store=True)
        date_hired = fields.Date('Date Hired', store=True)
        separation_date = fields.Date('Separation Date', store=True)
        separation_status_id = fields.Many2one('cs.portal.separation.status', string='Separation Status', store=True)
        category = fields.Selection([('authorized', 'Authorized'), ('desired', 'Desired'), ('undesired', 'Undesired')], 'Category', store=True)
        voluntary_involuntary = fields.Selection([('involuntary', 'INVOLUNTARY'), ('voluntary', 'VOLUNTARY')], 'Voluntary/Involuntary', store=True)
        # reason_for_separation_id = fields.Many2one('cs.portal.reason.for.separation', string='Reason For Separation (Resignation Letter/ Termination notice)', store=True)
        hr_remarks = fields.Char('HR Detailed Remarks', store=True)
        date_uploaded = fields.Date('Date Uploaded', store=True)
        account_owner_id = fields.Many2one('cs.portal.account.owner', string='Owner', index=True)
        initial_approach_date = fields.Date('Initial Approach Date', store=True)
        client_agreed_to_backfill = fields.Selection([('yes', 'YES'), ('no', 'NO')], 'Client Agreed to Backfill?', store=True)
        initial_remarks = fields.Char('Initial Remarks', store=True)
        Progress_remarks = fields.Text('Progress Remarks')
        backfill_req_date = fields.Date('Odoo Backfill Requisition Date', store=True)

    class CSPortal_Separation_Status(models.Model):
        _name = 'cs.portal.separation.status'
        _description = 'Separation Status'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Separation Status', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Separation Status already exists!'),
        ]

    class CSPortal_Reason_For_Separation(models.Model):
        _name = 'cs.portal.reason.for.separation'
        _description = 'REASON For Separation (Resignation Letter/ Termination notice)'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Reason for Separation (Resignation Letter/ Termination notice) ', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Reason for Separation already exists!'),
        ]

    class CSPortal_Requisition(models.Model):
        _name = 'cs.portal.requisition'
        _description = 'CS Portal Requisition'
        _rec_name = 'id'

        active = fields.Boolean(default=True)
        cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
        x_job_description = fields.Binary(string='Job Description', attachment=True, store=True)
        jd_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                            relation='m2m_ir_requisition_attachment_rel',
                                            column1='m2m_id',
                                            column2='attachment_id',
                                            string='Job Description')
        calibration_date = fields.Date(string='Calibration Date', store=True)
        start_date = fields.Date(string='Start Date', store=True)
        position_classification = fields.Selection([('growth', 'Growth'), ('backfill', 'Backfill')], 'Position Classification', store=True)
        client_classification = fields.Selection(
        [('new', 'New'), ('existing', 'Existing'), ('sales', 'Sales'), ('support hiring', 'Support Hiring')],
        string='Client Classification', store=True)
        job_title_name = fields.Char(string='Job Title')
        
        hiring_manager = fields.Char(string='Hiring Manager', store=True)
        client_validation = fields.Binary(string='Client Validation', attachment=True, store=True)
        client_validation_attachment_ids = fields.Many2many(comodel_name='ir.attachment',
                                            relation='m2m_ir_requisition_attachment_rel',
                                            column1='m2m_id',
                                            column2='attachment_id',
                                            string='Client Validation')
    
    class CSPortal_Revenue_Generation(models.Model):
        _name = 'cs.portal.revenue.generation'
        _description = 'CS Portal Revenue Generation'
        _rec_name = 'id'

        active = fields.Boolean(default=True)
        cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main', store=True)
        type_of_revenue_generation_id = fields.Many2one('cs.portal.revenue.generation.type', 'Revenue Generation Type', store=True)
        # type_of_revenue_generation_ids = fields.Many2many('cs.portal.revenue.generation.type','cs_portal_revenue_generation_rel','revenue_generation_id','type_id', string='Revenue Generation Types', store=True)
        revenue_generation_details_ids = fields.One2many('cs.portal.revenue.generation.details','revenue_generation_id', string='Revenue Generation Details')
        # record_relation = fields.Integer(string="Record Relation", store=True)
        record_relation = fields.Integer(string="Record Relation", related="cs_portal_main_id.record_id", store=True)
        revenue_generation_type_id = fields.Many2one('cs.portal.main', 'Type of Revenue Generation', store=True)
        cs_main_ref_id = fields.Many2one('cs.portal.main', string='CS Main Ref', compute="_compute__cs_portal_main_id", store=True)
        cs_main_identifier_id = fields.Many2one('cs.portal.main', string='CS Main Identifier', compute="_compute__cs_portal_main_id", store=True)
        
        @api.depends('cs_portal_main_id')
        def _compute__cs_portal_main_id(self):
            for record in self:
                record.cs_main_ref_id = record.cs_portal_main_id.id
                record.cs_main_identifier_id = record.cs_portal_main_id.id
        
        #Bonus and incentives
        amount_usd = fields.Float('Amount in $', store=True)
        employee_name = fields.Char('Employee Name', store=True)
        requested_date = fields.Date('Requested Date', store=True)
        amount_php = fields.Float('Amount in ₱', store=True)

        #GLOC Courses/Services
        course_title = fields.Char('Course Title/Service Provided', store=True)
        price_per_course = fields.Float('Price per Course/Service', store=True)
        invoiced_month = fields.Char('Invoiced Month', store=True)

        #New Equipment
        it_assets = fields.Char('IT Assets/Peripheral', store=True)
        quantity = fields.Integer('Quantity', store=True)
        order_date = fields.Date('Order Date', store=True)
        order_status = fields.Selection([('pending', 'Pending'), ('ordered', 'Ordered'), ('received', 'Received'),('awaiting_delivery', 'Awaiting Delivery')], 'Order Status', store=True)

        #Others
        purpose = fields.Char('Purpose', store=True)
        completed_date = fields.Date('Closed-Completed Date', store=True)

        #Procurement
        miscellaneous = fields.Char('Miscellaneous', store=True)
        approval_status = fields.Selection([('dissaprove', 'Dissaprove'), ('approve', 'Approve'), ], 'Approval Status', store=True)

        #Salary Increase

        #Teambuilding
        employee_list = fields.Integer('List of Employees Included', store=True)
        approval_date = fields.Date('Approval Date', store=True)

        #Travel
        destination = fields.Char('Destination', store=True)

        # readonly_bonus_incentive_fields = fields.Boolean(string='Readonly Bonus Incentive Fields', compute='_compute_readonly_fields', store=True)
        readonly_bonus_incentive_fields = fields.Boolean(string='Readonly Bonus Incentive Fields', store=True)

        is_readonly = fields.Boolean(string='Revenue Generation Type', store=True)
        # is_readonly = fields.Boolean(string='Revenue Generation Type', compute='_compute_is_readonly', store=True)
        # @api.depends('type_of_revenue_generation_id')
        # def _compute_is_readonly(self):
        #     for record in self:
        #         if record.type_of_revenue_generation_id.id == 1: 
        #             record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 2: 
        #                 record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 3:  
        #                 record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 4:  
        #                 record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 5: 
        #                 record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 6: 
        #                 record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 7:  
        #                 record.is_readonly = True
        #         elif record.type_of_revenue_generation_id.id == 8:  
        #                 record.is_readonly = True
        #         else:
        #             record.is_readonly = False
        
        # @api.depends('type_of_revenue_generation_id')
        # def _compute_is_readonly(self):
        #     readonly_type_ids = [1]
        #     for record in self:
        #         record.is_readonly = record.type_of_revenue_generation_id.id in readonly_type_ids

        # @api.depends('type_of_revenue_generation_id')
        # def _compute_is_readonly(self):
        #     for record in self:
        #         if record.type_of_revenue_generation_id.name in ['Bonus & Incentive', 'GLOC Courses/Services', 'New Equipment', 'Others', 'Procurement', 'Salary Increase', 'Team Building', 'Travel' ]:
        #             record.is_readonly = True
        #         else:
        #             record.is_readonly = False


    # @api.onchange('type_of_revenue_generation_id')
    # def _compute_readonly_fields(self):
    #     for record in self:
    #         if record.type_of_revenue_generation_id.name == 'Bonus & Incentive':
    #             record.readonly_bonus_incentive_fields = True
    #         else:
    #             record.readonly_bonus_incentive_fields = False

    # @api.onchange('type_of_revenue_generation_ids')
    # def _onchange_type_of_revenue_generation_ids(self):
    #     if self.type_of_revenue_generation_ids:
    #         existing_types = self.revenue_generation_details_ids.mapped('type_id')
    #         new_details = [
    #             (0, 0, {'type_id': type_id.id})
    #             for type_id in self.type_of_revenue_generation_ids - existing_types]
    #         self.revenue_generation_details_ids = new_details

    class CSPortal_Client_Revenue_Generation_Type(models.Model):
        _name = 'cs.portal.revenue.generation.type'
        _description = 'CS Portal Revenue Generation Type'
        _rec_name = 'name'

        active = fields.Boolean(default=True)
        name = fields.Char('Type of Revenue Generation', store=True, required=True)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Type of Revenue Generation already exists!'),
        ]

    class CSPortal_Revenue_Generation_Details(models.Model):
        _name = 'cs.portal.revenue.generation.details'
        _description = 'Revenue Generation Details'

        active = fields.Boolean(default=True)
        revenue_generation_id = fields.Many2one('cs.portal.revenue.generation', string='Revenue Generation', ondelete='cascade')
        type_id = fields.Many2one('cs.portal.revenue.generation.type', string='Type of Revenue Generation', required=True)
        
        # Common fields
        # amount = fields.Float(string='Amount')
        # description = fields.Text(string='Description')
        
        # Fields specific to Bonus and Incentives
        amount_usd = fields.Float('Amount in $', store=True)
        employee_name = fields.Char('Employee Name', store=True)
        requested_date = fields.Date('Requested Date', store=True)
        amount_php = fields.Float('Amount in ₱', store=True)
    
        # Fields specific to New Equipment
        it_assets = fields.Char('IT Assets/Peripheral', store=True)
        quantity = fields.Integer('Quantity', store=True)
        order_date = fields.Date('Order Date', store=True)
        order_status = fields.Selection([('pending', 'Pending'), ('ordered', 'Ordered'), ('received', 'Received')], 'Order Status', store=True)
        
        # Compute visibility of fields
    # @api.onchange('type_id')
    # def _onchange_type_id(self):
    #     if self.type_id.name == 'Bonus & Incentive':
    #         self.employee_name = False
    #         self.amount_php = 0.0
    #         self.it_assets = False
    #         self.quantity = 0
    #         self.order_date = False
    #         self.order_status = False
    #     elif self.type_id.name == 'New Equipment':
    #         self.amount_usd = 0.0
    #         self.requested_date = False
    
    # class CSPortal_Bonus_and_Incentive(models.Model):
    #     _name = 'cs.portal.bonus.and.incentive'
    #     _description = 'CS Portal Chat Platform'
    #     _rec_name = 'name'

    #     def _get_default_color(self):
    #         return randint(1, 11)

    #     active = fields.Boolean(default=True)
    #     name = fields.Char('Chat Platform', required=True, translate=True)
    #     color = fields.Integer('Color', default=_get_default_color)
        
    class CSPortal_Chat_Platform(models.Model):
        _name = 'cs.portal.chat.platform'
        _description = 'CS Portal Chat Platform'
        _rec_name = 'name'

        def _get_default_color(self):
            return randint(1, 11)

        active = fields.Boolean(default=True)
        name = fields.Char('Chat Platform', required=True, translate=True)
        color = fields.Integer('Color', default=_get_default_color)

        _sql_constraints = [
            ('name_uniq', 'unique (name)', 'Chat Platform already exists!'),
        ]

    