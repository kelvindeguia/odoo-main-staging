import pytz

from odoo import api, fields, models, tools, SUPERUSER_ID
from datetime import datetime, date, timezone
from datetime import timedelta

class Requisition(models.Model):
    _name = "hr.requisition"
    _description = "Requisition"
    _rec_name = 'x_req_id'

    active = fields.Boolean("Active", default=True, help="If the active field is set to false, it will allow you to hide the case without removing it.")
    cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
    x_req_id = fields.Char('Requisition ID', store=True, required=True)
    x_department_id = fields.Many2one('hr.department', string='Client Name', store=True)
    x_job_name = fields.Many2one('hr.job', string='Job Title', store=True)
    x_recruitment_manager = fields.Selection(
        [('erma_san_miguel', 'Erma San Miguel'), ('rodney ynares', 'Rodney Ynares'),
         ('alekcie vergara', 'Alekcie Vergara'), ('cesar jules van cayabat', 'Cesar Jules Van Cayabat'),
         ('erlyn ferrer', 'Erlyn Ferrer')],
        string="Recruitment Manager", store=True)
    x_assigned_recruiter = fields.Selection(
        [('christian anonuevo', 'Christian Anonuevo'), ('paul anthony cruz', 'Paul Anthony Cruz'),
         ('nemuel pamplona', 'Nemuel Pamplona'), ('maurene garcia', 'Maurene Garcia'), ('ronald dayon dayon', 'Ronald Dayon Dayon'),
         ('charina juanitas', 'Charina Juanitas'), ('reina yago', 'Reina Yago'), ('vincent soriano', 'Vincent Soriano'), ('nicole tugangui', 'Nicole Tugangui')],
        string="Assigned Recruiter", store=True)
    x_remaining_vacancy = fields.Integer(string='Remaining Vacancy', store=True)
    x_filled = fields.Integer(string='Filled', store=True)
    x_no_of_demand = fields.Integer(string='Headcount Demand', store=True)
    x_salary_package = fields.Char(string='Salary Package', store=True)
    x_hiring_manager = fields.Char(string='Hiring Manager', store=True)
    x_hiring_manager_email = fields.Char(string='Hiring Manager Email Address', store=True)
    x_calibration_call_availability = fields.Datetime(string='Calibration Availability for Calibration Call', store=True)
    x_recruitment_requestor = fields.Selection(
        [('effy bongco', 'Effy Bongco'), ('wendy panuelos', 'Wendy Panuelos'),
         ('emir delos santos', 'Emir Delos Santos'), ('zack concepcion', 'Zack Concepcion'),
         ('mariebien custodio', 'Mariebien Custodio'), ('thea vivar', 'Thea Vivar'), ('lovely villafranca', 'Lovely Villafranca'),
         ('tamara bautista', 'Tamara Bautista'), ('support hiring', 'Support Hiring'),
         ('maximillian adrian christian venida', 'Maximillian Adrian Christian Venida'), ('grace_lu', 'Grace Lu'), ('gloc', 'GLOC'),
         ('patrick arandia', 'Patrick Arandia'), ('paula fernandez', 'Paula Kris Fernandez'), ('lisa ward', 'Lisa Ward')], string="Requestor",
        store=True)
    x_recruitment_support_team = fields.Char(string='Support Team', store=True)
    x_attachment_base = fields.Many2many(comodel_name="ir.attachment",
                                         relation="requisition_attachment",
                                         column1="req_id", column2="attachment_id", string="Attachment")
    x_calibration_notes = fields.Binary(string='Calibration Notes', attachment=True, store=True)
    calibration_notes_file_name = fields.Char('Calibration Notes File Name', store=True)
    calibration_notes_ids = fields.Many2many(comodel_name='ir.attachment',
                                    relation='m2m_ir_calibration_notes_rel',
                                    column1='m2m_id',
                                    column2='attachment_id',
                                    string='Calibration Notes')
    x_job_description = fields.Binary(string='Job Description', attachment=True, store=True)
    x_job_description_filename = fields.Char(string='Job Description Filename', store=True)
    job_description_ids = fields.Many2many(comodel_name='ir.attachment', 
                                           required=True,
                                           relation='m2m_ir_job_description_rel',
                                           column1='m2m_id',
                                           column2='attachment_id',
                                           string='Job Description')
    job_description_file_name = fields.Char('Job Description File Name', store=True)
    x_client_classification = fields.Selection(
        [('new', 'New'), ('existing', 'Existing'), ('sales', 'Sales'), ('support hiring', 'Support Hiring')],
        string='Client Classification', store=True)
    x_requisition_status = fields.Selection(
        [('pending', 'For Calibration'),
         ('open', 'Open'),
         ('reopen', 'Reopened'),
         ('in progress', 'Ongoing Sourcing'),
         ('on hold', 'On Hold'),
         ('cancelled', 'Cancelled'),
         ('recalibrate', 'Recalibrate'),
         ('filled', 'Filled'),
         ('closed', 'Completed')],
        string='Requisition Status', default='pending', store=True)
    x_onhold_cancelled_remarks = fields.Text(string='Remarks', store=True)
    cancelled_reason = fields.Selection([('pro_active', 'Pro-Active'), ('abandoned', 'Abandoned')],
                                            'Cancelled Reason', store=True)
    x_req_sla = fields.Integer(string='Number of Days Passed')
    x_req_sla_total = fields.Integer(string='Number of Days Passed')
    x_date_today = fields.Datetime(string='Date Today')
    x_onhold_days = fields.Integer(string='Onhold Days', store=True)
    x_onhold_start_date = fields.Datetime(string='Onhold Start Date', store=True)
    x_onhold_end_date = fields.Datetime(string='Onhold End Date', store=True)
    x_old_onhold_checker = fields.Integer(string='Old Onhold Checker', store=True)
    x_onhold_counter = fields.Integer(string='Onhold Counter')
    x_department_name = fields.Char(string='Client Name')
    x_requisition_url = fields.Text(string='Requisition URL')
    x_onhold_logs = fields.Text(string='Onhold Logs', store=True)
    x_applicants_id = fields.Many2one('hr.applicant', string='Applications', store=True)
    x_days_passed = fields.Selection(
        [('less_than_30_days', 'Less than 30 days'), ('passed_30_days', 'Passed 30 days')], 'Days Passed', store=True)
    x_job_classification = fields.Selection([('generic', 'Generic'), ('tech', 'Tech'), ('niche', 'Niche'), ('executive', 'Executive')],
                                            'Job Classification', store=True)
    x_industry = fields.Selection(
        [('back office', 'Back Office'), ('customer service', 'Customer Service'), ('digital', 'Digital'),
         ('finance', "Finance"), ('medical', 'Medical'), ('operations support', 'Operations Support'),
         ('sales', 'Sales'), ('supply chain', 'Supply Chain'), ('tech', 'Tech')], 'Industry', store=True)
    x_req_position_classification = fields.Selection(
        [('growth', 'Growth'), ('new', 'New'), ('backfill', 'Backfill'), ('support hiring', 'Support Hiring')],
        string='Position Classification', store=True)
    x_date_opened = fields.Char('Ongoing Sourcing Date', store=True)
    sourcing_date = fields.Date('Ongoing Sourcing Date', store=True)
    calibration_date = fields.Date(string='Calibration Date', store=True)
    company = fields.Selection(
        [('aiic', 'AIIC'), ('iswerk', 'ISWERK')], string="Company",
        store=True)
    start_date = fields.Date(string='Start Date', store=True)
    applicant_ids = fields.One2many('hr.applicant', 'x_requisition_id', 'Applicants', store=True)
    stage_id = fields.Many2one('hr.recruitment.stage', string='Stage')

    # QuickSight Fields
    qs_department_name = fields.Char(string='QS Client Name', store=True)
    qs_job_title = fields.Char(string='QS Job Title', store=True)

    # TA Live File Additional Fields
    career_level = fields.Selection([('rank_and_file', 'Rank and File'), ('managerial', 'Managerial')], string="Career Level", store=True)
    date_cancelled = fields.Datetime('Date Cancelled', store=True)
    date_onhold = fields.Datetime('Date Onhold', store=True)
    date_filled = fields.Datetime('Date Filled', store=True)
    date_reopen = fields.Datetime('Date Reopen', store=True)
    audio_clip_needed = fields.Boolean('Audio Clip Needed?', store=True)
    assessment_needed = fields.Boolean('Assessment Needed?', store=True)
    projected_headcount = fields.Integer('Projected Headcount to Close', store=True)
    projected_neo_date = fields.Date('Projected NEO Date', store=True)
    requisition_remarks = fields.Html('Requisition Remarks', store=True)
    sla_met = fields.Selection([('no', 'No'), ('yes', 'Yes')], 'SLA Met?', store=True)
    days_to_fill = fields.Integer('Days to Fill', store=True)
    client_website = fields.Char('Client Website', store=True)
    testing_datetime = fields.Datetime('Testing Datetime', store=True)
    company_website = fields.Char('Company Website', store=True)

    # SLA Fields
    date_source = fields.Datetime('Date Source', store=True)
    end_date = fields.Datetime('End Date', store=True)
    days_ageing = fields.Integer('Days Ageing')
    hold_counter = fields.Integer('Hold Counter', store=True)

     #New SLA Fields
    req_ageing = fields.Integer('Requisition Ageing')
    req_ageing_total = fields.Integer('Requisition Ageing')
    days_onhold = fields.Integer('Total Days Onhold', store=True)
    hold_start_date = fields.Datetime(string='Onhold Start Date', store=True)
    hold_end_date = fields.Datetime(string='Onhold End Date', store=True)
    old_onhold_checker = fields.Integer(string='Old Onhold Checker', store=True)
    onhold_counter = fields.Integer(string='Onhold Counter')

    # Additional Items
    sec_hiring_manager = fields.Char(string='Secondary Hiring Manager POC', store=True)
    calibration_needed = fields.Boolean('Calibration Needed?', store=True)
    priority = fields.Selection([('no','No'),('yes','Yes')], groups="hr_recruitment.group_hr_recruitment_manager", string="Priority", store=True)

    record_name = fields.Char(string='Record Name', compute="_compute_record_id", store=True)
    record_id = fields.Integer(string="Record ID", compute="_compute_record_id", store=True)
    # save = fields.Boolean('Save', default=False, store=True)

    # @api.model
    # def create(self, vals):
    #     record = super(Requisition, self).create(vals)
    #     if record.x_job_description and record.cs_portal_main_id:
    #         self._create_attachment(record)
    #     return record

    # def write(self, vals):
    #     res = super(Requisition, self).write(vals)
    #     for record in self:
    #         if 'x_job_description' in vals and record.cs_portal_main_id:
    #             self._create_attachment(record)
    #     return res

    # def _create_attachment(self, record):
    #     attachment_name = record.x_job_description_filename or 'Job Description'
    #     attachment = self.env['ir.attachment'].create({
    #         'name': attachment_name,
    #         'type': 'binary',
    #         'datas': record.x_job_description,
    #         'res_model': 'cs.portal.main',
    #         'res_id': record.cs_portal_main_id.id,
    #     })
    #     record.cs_portal_main_id.jd_attachment_ids = [(4, attachment.id)]

    #Requisition Logs
    @api.depends('x_req_id')
    def _compute_record_id(self):
        for record in self:
            if not record.record_id:
                record.record_id = record.id
                record.record_name = record.x_req_id

    # Requisition Information

    @api.onchange('x_department_id')
    def x_department_id_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_department_id != record._origin.x_department_id:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_department_id.name, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_department_id.name,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'many2one',
                        'updated_field': "Client Name",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_job_name')
    def x_job_name_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_job_name != record._origin.x_job_name:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_job_name.name, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_job_name.name,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'many2one',
                        'updated_field': "Job Title",
                        'related_record': record.record_name,
                    })
                
    @api.onchange('x_job_description')
    def x_job_description_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_job_description != record._origin.x_job_description:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_job_description, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_job_description,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'binary',
                        'updated_field': "Job Description",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })
                
    @api.onchange('x_calibration_notes')
    def x_calibration_notes_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_calibration_notes != record._origin.x_calibration_notes:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.calibration_notes_file_name, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.calibration_notes_file_name,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'binary',
                        'updated_field': "Calibration Notes",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('company')
    def company_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.company != record._origin.company:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.company, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.company,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Company",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('career_level')
    def career_level_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.career_level != record._origin.career_level:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.career_level, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.career_level,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Career Level",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('audio_clip_needed')
    def audio_clip_needed_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.audio_clip_needed != record._origin.audio_clip_needed:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.audio_clip_needed, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.audio_clip_needed,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'boolean',
                        'updated_field': "Audio Clip Needed?",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('assessment_needed')
    def assessment_needed_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.assessment_needed != record._origin.assessment_needed:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.assessment_needed, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.assessment_needed,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'boolean',
                        'updated_field': "Assessment Needed?",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('priority')
    def priority_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.priority != record._origin.priority:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.priority, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.priority,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Priority",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('calibration_needed')
    def calibration_needed_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.calibration_needed != record._origin.calibration_needed:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.calibration_needed, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.calibration_needed,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'boolean',
                        'updated_field': "Calibration Needed?",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_calibration_call_availability')
    def x_calibration_call_availability_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_calibration_call_availability != record._origin.x_calibration_call_availability:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_calibration_call_availability, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_calibration_call_availability,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Calibration Availability for Calibration Call",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('calibration_date')
    def calibration_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.calibration_date != record._origin.calibration_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.calibration_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.calibration_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'date',
                        'updated_field': "Calibration Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('start_date')
    def start_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.start_date != record._origin.start_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.start_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.start_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'date',
                        'updated_field': "Start Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_client_classification')
    def x_client_classification_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_client_classification != record._origin.x_client_classification:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_client_classification, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_client_classification,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Client Classification",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_job_classification')
    def x_job_classification_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_job_classification != record._origin.x_job_classification:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_job_classification, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_job_classification,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Job Classification",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_req_position_classification')
    def x_req_position_classification_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_req_position_classification != record._origin.x_req_position_classification:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_req_position_classification, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_req_position_classification,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Position Classification",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_industry')
    def x_industry_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_industry != record._origin.x_industry:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_industry, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_industry,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Industry",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_salary_package')
    def x_salary_package_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_salary_package != record._origin.x_salary_package:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_salary_package, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_salary_package,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Salary Package",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('client_website')
    def client_website_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.client_website != record._origin.client_website:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.client_website, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.client_website,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Client Website",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })
    
    # Requisition SLA and Status
    
    @api.onchange('x_req_id')
    def x_req_id_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_req_id != record._origin.x_req_id:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_req_id, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_req_id,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Requisition ID",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_requisition_status')
    def x_requisition_status_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_requisition_status != record._origin.x_requisition_status:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_requisition_status, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_requisition_status,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Requisition Status",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('date_filled')
    def date_filled_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.date_filled != record._origin.date_filled:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.date_filled, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.date_filled,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Date Filled",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_date_opened')
    def x_date_opened_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_date_opened != record._origin.x_date_opened:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_date_opened, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_date_opened,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Ongoing Sourcing Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('sourcing_date')
    def sourcing_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.sourcing_date != record._origin.sourcing_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.sourcing_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.sourcing_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'date',
                        'updated_field': "Ongoing Sourcing Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('date_source')
    def date_source_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.date_source != record._origin.date_source:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.date_source, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.date_source,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Date Source",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('end_date')
    def end_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.end_date != record._origin.end_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.end_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.end_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "End Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })
                
    @api.onchange('hold_counter')
    def hold_counter_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.hold_counter != record._origin.hold_counter:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.hold_counter, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.hold_counter,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Hold Counter",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_onhold_cancelled_remarks')
    def x_onhold_cancelled_remarks_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_onhold_cancelled_remarks != record._origin.x_onhold_cancelled_remarks:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_onhold_cancelled_remarks, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_onhold_cancelled_remarks,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'text',
                        'updated_field': "Remarks",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_req_sla_total')
    def x_req_sla_total_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_req_sla_total != record._origin.x_req_sla_total:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_req_sla_total, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_req_sla_total,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Numbers of Days Passed",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })
                
    @api.onchange('x_onhold_days')
    def x_onhold_days_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_onhold_days != record._origin.x_onhold_days:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_onhold_days, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_onhold_days,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Onhold Days",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_onhold_start_date')
    def x_onhold_start_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_onhold_start_date != record._origin.x_onhold_start_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_onhold_start_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_onhold_start_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Onhold Start Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_onhold_end_date')
    def x_onhold_end_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_onhold_end_date != record._origin.x_onhold_end_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_onhold_end_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_onhold_end_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Onhold End Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_old_onhold_checker')
    def x_old_onhold_checker_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_old_onhold_checker != record._origin.x_old_onhold_checker:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_old_onhold_checker, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_old_onhold_checker,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Old Onhold Checker",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('req_ageing')
    def req_ageing_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.req_ageing != record._origin.req_ageing:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.req_ageing, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.req_ageing,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Requisition Ageing",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('days_onhold')
    def days_onhold_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.days_onhold != record._origin.days_onhold:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.days_onhold, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.days_onhold,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Total Days Onhold",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('hold_start_date')
    def hold_start_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.hold_start_date != record._origin.hold_start_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.hold_start_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.hold_start_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Onhold Start Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('hold_end_date')
    def hold_end_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.hold_end_date != record._origin.hold_end_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.hold_end_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.hold_end_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Onhold End Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('old_onhold_checker')
    def hold_onhold_checker_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.old_onhold_checker != record._origin.old_onhold_checker:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.old_onhold_checker, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.old_onhold_checker,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Old Onhold Checker",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('hold_end_date')
    def hold_end_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.hold_end_date != record._origin.hold_end_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.hold_end_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.hold_end_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'datetime',
                        'updated_field': "Onhold End Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })
    
    # Staffing Overview

    @api.onchange('x_no_of_demand')
    def x_no_of_demand_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_no_of_demand != record._origin.x_no_of_demand:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_no_of_demand, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_no_of_demand,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Headcount Demand",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_filled')
    def x_filled_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_filled != record._origin.x_filled:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_filled, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_filled,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Filled",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('projected_headcount')
    def projected_headcount_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.projected_headcount != record._origin.projected_headcount:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.projected_headcount, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.projected_headcount,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'integer',
                        'updated_field': "Projected Headcount to Close",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('projected_neo_date')
    def projected_neo_date_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.projected_neo_date != record._origin.projected_neo_date:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.projected_neo_date, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.projected_neo_date,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'date',
                        'updated_field': "Projected NEO Date",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    # Recruitment and Client POC

    @api.onchange('x_recruitment_requestor')
    def x_recruitment_requestor_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_recruitment_requestor != record._origin.x_recruitment_requestor:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_recruitment_requestor, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_recruitment_requestor,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Requestor",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_hiring_manager')
    def x_hiring_manager_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_hiring_manager != record._origin.x_hiring_manager:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_hiring_manager, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_hiring_manager,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Hiring Manager",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('sec_hiring_manager')
    def sec_hiring_manager_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.sec_hiring_manager != record._origin.sec_hiring_manager:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.sec_hiring_manager, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.sec_hiring_manager,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Secondary Hiring Manager POC",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_hiring_manager_email')
    def x_hiring_manager_email_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_hiring_manager_email != record._origin.x_hiring_manager_email:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_hiring_manager_email, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_hiring_manager_email,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'char',
                        'updated_field': "Hiring Manager Email Address",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('x_recruitment_manager')
    def x_recruitment_manager_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.x_recruitment_manager != record._origin.x_recruitment_manager:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.x_recruitment_manager, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.x_recruitment_manager,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Recruitment Manager",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })

    @api.onchange('assigned_recruiter_id')
    def assigned_recruiter_id_onchange_logs(self):
        for record in self:
            if record.record_id:
                if record.assigned_recruiter_id != record._origin.assigned_recruiter_id:
                    new_log = self.env['hr.logs'].create({
                        'ov_char': record._origin.assigned_recruiter_id, #add .name or the _rec name of the model if the field is many2one
                        'nv_char': record.assigned_recruiter_id,
                        'requisition_related_record_id': record.record_id,
                        'related_model': 'hr.requisition',
                        'field_type': 'selection',
                        'updated_field': "Assigned Recruiter",
                        'record_name': "requisition_related_record_id",
                        'related_record': record.record_name,
                    })
    
    # Update Logs Continuation
    update_logs = fields.Text(string="Update Logs", store=True, default="")
    # updated_by = fields.Text(string="Updated By", store=True)

    @api.onchange('x_department_id')
    def _onchange_fields_update_client_name(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Client Name
                if self.x_department_id != self._origin.x_department_id:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Client Name | Old: {self._origin.x_department_id.name} | New: {self.x_department_id.name}\n"

    # Requisition Information

    @api.onchange('x_job_name')
    def _onchange_fields_update_job_title(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Job Title
                if self.x_job_name != self._origin.x_job_name:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Job Title | Old: {self._origin.x_job_name.name} | New: {self.x_job_name.name}\n"
    
    @api.onchange('x_job_description')
    def _onchange_fields_update_job_description(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Job Description
                if self.x_job_description != self._origin.x_job_description:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Job Description | Old: {self._origin.job_description_file_name} | New: {self.job_description_file_name}\n" 
    
    @api.onchange('x_calibration_notes')
    def _onchange_fields_update_calibration_notes(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Calibration Notes
                if self.x_calibration_notes != self._origin.x_calibration_notes:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Calibration Notes | Old: {self._origin.calibration_notes_file_name} | New: {self.calibration_notes_file_name}\n"

    @api.onchange('company')
    def _onchange_fields_update_company(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Company
                if self.company != self._origin.company:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Company | Old: {self._origin.company} | New: {self.company}\n"

    @api.onchange('career_level')
    def _onchange_fields_update_career_level(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Career Level
                if self.career_level != self._origin.career_level:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Career Level | Old: {self._origin.career_level} | New: {self.career_level}\n"

    @api.onchange('audio_clip_needed')
    def _onchange_fields_update_clip_needed(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Audio Clip Needed
                if self.audio_clip_needed != self._origin.audio_clip_needed:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Audio Clip Needed | Old: {self._origin.audio_clip_needed} | New: {self.audio_clip_needed}\n"

    @api.onchange('assessment_needed')
    def _onchange_fields_update_assessment_needed(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Assessment Needed
                if self.assessment_needed != self._origin.assessment_needed:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Assessment Needed | Old: {self._origin.assessment_needed} | New: {self.assessment_needed}\n"

    @api.onchange('calibration_needed')
    def _onchange_fields_update_calibration_needed(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Calibration Needed
                if self.calibration_needed != self._origin.calibration_needed:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Calibration Needed | Old: {self._origin.calibration_needed} | New: {self.calibration_needed}\n"

    @api.onchange('priority')
    def _onchange_fields_update_priority(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Priority
                if self.priority != self._origin.priority:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Priority | Old: {self._origin.priority} | New: {self.priority}\n"

    @api.onchange('x_calibration_call_availability')
    def _onchange_fields_update_calibration_availability(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Calibration Availability
                if self.x_calibration_call_availability != self._origin.x_calibration_call_availability:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Calibration Availability | Old: {self._origin.x_calibration_call_availability} | New: {self.x_calibration_call_availability}\n"

    @api.onchange('calibration_date')
    def _onchange_fields_update_calibration_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Calibration Date
                if self.calibration_date != self._origin.calibration_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Calibration Date | Old: {self._origin.calibration_date} | New: {self.calibration_date}\n"

    @api.onchange('start_date')
    def _onchange_fields_update_start_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Start Date
                if self.start_date != self._origin.start_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Start Date | Old: {self._origin.start_date} | New: {self.start_date}\n"

    @api.onchange('x_client_classification')
    def _onchange_fields_update_client_classification(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Client Classification
                if self.x_client_classification != self._origin.x_client_classification:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Client Classification | Old: {self._origin.x_client_classification} | New: {self.x_client_classification}\n"

    @api.onchange('x_job_classification')
    def _onchange_fields_update_job_classification(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Job Classification
                if self.x_job_classification != self._origin.x_job_classification:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Job Classification | Old: {self._origin.x_job_classification} | New: {self.x_job_classification}\n"

    @api.onchange('x_req_position_classification')
    def _onchange_fields_update_position_classification(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Position Classification
                if self.x_req_position_classification != self._origin.x_req_position_classification:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Position Classification | Old: {self._origin.x_req_position_classification} | New: {self.x_req_position_classification}\n"

    @api.onchange('x_industry')
    def _onchange_fields_update_industry(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Industry
                if self.x_industry != self._origin.x_industry:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Industry | Old: {self._origin.x_industry} | New: {self.x_industry}\n"

    @api.onchange('x_salary_package')
    def _onchange_fields_update_salary_package(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Salary Package
                if self.x_salary_package != self._origin.x_salary_package:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Salary Package | Old: {self._origin.x_salary_package} | New: {self.x_salary_package}\n"

    @api.onchange('client_website')
    def _onchange_fields_update_client_website(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Client Website
                if self.client_website != self._origin.client_website:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Client Website | Old: {self._origin.client_website} | New: {self.client_website}\n"

    # Requisition SLA and Status

    @api.onchange('x_requisition_status')
    def _onchange_fields_update_requisition_status(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Requisition Status
                if self.x_requisition_status != self._origin.x_requisition_status:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Requistion Status | Old: {self._origin.x_requisition_status} | New: {self.x_requisition_status}\n"

    @api.onchange('date_cancelled')
    def _onchange_fields_update_date_cancelled(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Date Cancelled
                if self.date_cancelled != self._origin.date_cancelled:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Date Cancelled: {self._origin.date_cancelled} to {self.date_cancelled}\n"

    @api.onchange('date_onhold')
    def _onchange_fields_update_date_onhold(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Date On Hold
                if self.date_onhold != self._origin.date_onhold:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Date On Hold | Old: {self._origin.date_onhold} | New: {self.date_onhold}\n"                

    @api.onchange('date_filled')
    def _onchange_fields_update_date_filled(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Date Filled
                if self.date_filled != self._origin.date_filled:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Date Filled | Old: {self._origin.date_filled} | New: {self.date_filled}\n"

    @api.onchange('date_reopen')
    def _onchange_fields_update_date_reopen(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Date Reopen
                if self.date_reopen != self._origin.date_reopen:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Date Reopen | Old: {self._origin.date_reopen} | New: {self.date_reopen}\n"

    @api.onchange('cancelled_reason')
    def _onchange_fields_update_cancelled_reason(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Cancelled Reason
                if self.cancelled_reason != self._origin.cancelled_reason:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Cancelled Reason | Old: {self._origin.cancelled_reason} | New: {self.cancelled_reason}\n"

    @api.onchange('x_date_opened')
    def _onchange_fields_update_date_opened(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Ongoing Sourcing Date
                if self.x_date_opened != self._origin.x_date_opened:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Ongoing Sourcing Date | Old: {self._origin.x_date_opened} | New: {self.x_date_opened}\n"

    @api.onchange('sourcing_date')
    def _onchange_fields_update_sourcing_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Ongoing Sourcing Date
                if self.sourcing_date != self._origin.sourcing_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Ongoing Sourcing Date | Old: {self._origin.sourcing_date} | New: {self.sourcing_date}\n"

    @api.onchange('testing_datetime')
    def _onchange_fields_update_testing_datetime(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Testing Datetime
                if self.testing_datetime != self._origin.testing_datetime:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Testing Datetime | Old: {self._origin.testing_datetime} | New: {self.testing_datetime}\n"

    @api.onchange('date_source')
    def _onchange_fields_update_date_source(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Date Source
                if self.date_source != self._origin.date_source:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Date Source | Old: {self._origin.date_source} | New: {self.date_source}\n"

    @api.onchange('end_date')
    def _onchange_fields_update_end_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # End Date
                if self.end_date != self._origin.end_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | End Date | Old: {self._origin.end_date} | New: {self.end_date}\n"

    @api.onchange('hold_counter')
    def _onchange_fields_update_hold_counter(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Hold Counter
                if self.hold_counter != self._origin.hold_counter:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Hold Counter | Old: {self._origin.hold_counter} | New: {self.hold_counter}\n"

    @api.onchange('x_onhold_cancelled_remarks')
    def _onchange_fields_update_cancelled_remarks(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Remarks
                if self.x_onhold_cancelled_remarks != self._origin.x_onhold_cancelled_remarks:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Remarks | Old: {self._origin.x_onhold_cancelled_remarks} | New: {self.x_onhold_cancelled_remarks}\n"

    @api.onchange('x_req_sla_total')
    def _onchange_fields_update_sla_total(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Number of Days Passed
                if self.x_req_sla_total != self._origin.x_req_sla_total:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Number of Days Passed | Old: {self._origin.x_req_sla_total} | New: {self.x_req_sla_total}\n"

    @api.onchange('x_onhold_days')
    def _onchange_fields_update_onhold_days(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Onhold Days
                if self.onhold_days != self._origin.onhold_days:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Onhold Days | Old: {self._origin.onhold_days} | New: {self.onhold_days}\n"

    @api.onchange('x_onhold_start_date')
    def _onchange_fields_update_onhold_start_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Onhold Start Date
                if self.x_onhold_start_date != self._origin.x_onhold_start_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Onhold Start Date | Old: {self._origin.x_onhold_start_date} | New: {self.x_onhold_start_date}\n"

    @api.onchange('x_onhold_end_date')
    def _onchange_fields_update_end_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Onhold End Date
                if self.x_onhold_end_date != self._origin.x_onhold_end_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Onhold End Date| Old: {self._origin.x_onhold_end_date} | New: {self.x_onhold_end_date}\n"

    @api.onchange('x_old_onhold_checker')
    def _onchange_fields_update_onhold_checker(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Old Onhold Checker
                if self.x_old_onhold_checker != self._origin.x_old_onhold_checker:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Old Onhold Checker | Old: {self._origin.x_old_onhold_checker} | New: {self.x_old_onhold_checker}\n"

    @api.onchange('x_onhold_counter')
    def _onchange_fields_update_onhold_counter(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Onhold Counter
                if self.x_onhold_counter != self._origin.x_onhold_counter:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Onhold Counter | Old: {self._origin.x_onhold_counter} | New: {self.x_onhold_counter}\n"

    @api.onchange('req_ageing')
    def _onchange_fields_update_req_ageing(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Requisition Ageing
                if self.req_ageing != self._origin.req_ageing:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Requisition Ageing | Old: {self._origin.req_ageing} | New: {self.req_ageing}\n"

    @api.onchange('req_ageing_total')
    def _onchange_fields_update_ageing_total(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Requisition Ageing Total
                if self.req_ageing_total != self._origin.req_ageing_total:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Requisition Ageing Total | Old: {self._origin.req_ageing_total} | New: {self.req_ageing_total}\n"

    @api.onchange('days_onhold')
    def _onchange_fields_update_days_onhold(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Total Days Onhold
                if self.days_onhold != self._origin.days_onhold:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Total Days Onhold | Old: {self._origin.days_onhold} | New: {self.days_onhold}\n"

    @api.onchange('hold_start_date')
    def _onchange_fields_update_hold_start(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Onhold Start Date
                if self.hold_start_date != self._origin.hold_start_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Onhold Start Date | Old: {self._origin.hold_start_date} | New: {self.hold_start_date}\n"

    @api.onchange('hold_end_date')
    def _onchange_fields_update_hold_end(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Onhold End Date
                if self.hold_end_date != self._origin.hold_end_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Onhold End Date | Old: {self._origin.hold_end_date} | New: {self.hold_end_date}\n"

    @api.onchange('old_onhold_checker')
    def _onchange_fields_update_onhold_checker(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Old Onhold Checker
                if self.old_onhold_checker != self._origin.old_onhold_checker:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Old Onhold Checker | Old: {self._origin.old_onhold_checker} | New: {self.old_onhold_checker}\n"
    
    #Staffing Overview

    @api.onchange('x_no_of_demand')
    def _onchange_fields_update_no_demand(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Headcount Demand
                if self.x_no_of_demand != self._origin.x_no_of_demand:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Headcount Demand | Old: {self._origin.x_no_of_demand} | New: {self.x_no_of_demand}\n"

    @api.onchange('x_filled')
    def _onchange_fields_update_x_filled(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Filled
                if self.x_filled != self._origin.x_filled:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Filled | Old: {self._origin.x_filled} | New: {self.x_filled}\n"
    
    @api.onchange('projected_headcount')
    def _onchange_fields_update_projected_headcount(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Projected Headcount to Close
                if self.projected_headcount != self._origin.projected_headcount:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Projected Headcount to Close | Old: {self._origin.projected_headcount} | New: {self.projected_headcount}\n"

    @api.onchange('projected_neo_date')
    def _onchange_fields_update_neo_date(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Projected NEO Date
                if self.projected_neo_date != self._origin.projected_neo_date:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Projected NEO Date | Old: {self._origin.projected_neo_date} | New: {self.projected_neo_date}\n"

    # Recruitment and Client POC

    @api.onchange('x_recruitment_requestor')
    def _onchange_fields_update_recruitment_requestor(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Requestor
                if self.x_recruitment_requestor != self._origin.x_recruitment_requestor:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Requestor | Old: {self._origin.x_recruitment_requestor} | New: {self.x_recruitment_requestor}\n"

    @api.onchange('x_hiring_manager')
    def _onchange_fields_update_hiring_manager(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Hiring Manager
                if self.x_hiring_manager != self._origin.x_hiring_manager:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Hiring Manager | Old: {self._origin.x_hiring_manager} | New: {self.x_hiring_manager}\n"

    @api.onchange('x_hiring_manager_email')
    def _onchange_fields_update_manager_email(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Hiring Manager Email Address
                if self.x_hiring_manager_email != self._origin.x_hiring_manager_email:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Hiring Manager Email Address | Old: {self._origin.x_hiring_manager_email} | New: {self.x_hiring_manager_email}\n"

    @api.onchange('x_recruitment_manager')
    def _onchange_fields_update_recruitment_manager(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Recruitment Manager
                if self.x_recruitment_manager != self._origin.x_recruitment_manager:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Recruitment Manager | Old: {self._origin.x_recruitment_manager.name} | New: {self.x_recruitment_manager.name}\n"

    @api.onchange('assigned_recruiter_id')
    def _onchange_fields_update_recruitment_recruiter(self):

        log_entry = ""
        user_name = self.env.user.name

        # Set Timezone
        user_timezone = 'Asia/Singapore'
        utc_now = datetime.utcnow()

        # Convert Time
        user_timezone = pytz.timezone(user_timezone)
        user_time = utc_now.astimezone(user_timezone)
        for record in self:
            # NAME
            if self._origin:  # check old value
                if self.update_logs == False:
                    self.update_logs = ""

                # Recruitment Manager
                if self.assigned_recruiter_id != self._origin.assigned_recruiter_id:
                    self.update_logs += f"{user_time:%m-%d-%Y %I:%M%p} | {user_name} | Recruitment Manager | Old: {self._origin.assigned_recruiter_id.name} | New: {self.assigned_recruiter_id.name}\n"

    @api.depends('write_uid')
    def _onchange_last_update(self):
        for rec in self:
            if rec.write_uid:
                if rec.updated_by != False:
                    rec.updated_by += f"Updated By: {self.write_uid.name}\n"
                else:
                    rec.updated_by = ""

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    x_requisition_id = fields.Many2one('hr.requisition', string='Requisition ID', store=True)

class UpdateLog(models.Model):
    _name = 'hr.updatelogs' 
    _description = 'Custom Log Model'
    _rec_name = 'x_log_record_name'


    x_log_record_name = fields.Char('Record Name', store=True)