from odoo import api, fields, models, tools, SUPERUSER_ID

class Logs(models.Model):
    _name = "hr.logs"
    _description = "Recruitment Logs"
    _order = "priority desc, id desc"
    _rec_name = "related_record"

    cs_portal_main_id = fields.Many2one('cs.portal.main', string='CS Portal Main')
    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    field_type = fields.Selection([('char', 'Char'), ('selection', 'Selection'), ('integer', 'Integer'), ('binary', 'Binary'),
                               ('boolean', 'Boolean'), ('float', 'Float'),
                               ('date', 'Date'), ('datetime', 'Datetime'),
                               ('text', 'Text'), ('many2one', 'Many2one')], "Field Type", store=True)
    # client_related_record_id = fields.Many2one('hr.department', 'Client Page Related Record', store=True)     
    # job_related_record_id = fields.Many2one('hr.job', 'Job Page Related Record', store=True)     
    requisition_related_record_id = fields.Many2one('hr.requisition', 'Requisition Page Related Record', store=True)     
    # applicant_related_record_id = fields.Many2one('hr.applicant', 'All Applicants Related Record', store=True)     
    priority = fields.Char('Priority', store=True)
    user_id = fields.Many2one('res.users', 'Responsible User', compute='_compute_user', store=True)
    updated_field = fields.Char('Updated Field', store=True)    
    record_name = fields.Char(string="Record Name", store=True)      
    related_model = fields.Char('Related Model', store=True)          
    related_record = fields.Char('Related Record', store=True)
    
    # Old values
    ov_integer = fields.Integer('Old Value Integer', store=True)
    ov_float = fields.Float('Old Value Float', store=True)
    ov_char = fields.Char('Old Value Char', store=True)
    ov_text = fields.Text('Old Value Text', store=True)
    ov_date = fields.Date('Old Value Date', store=True)
    ov_datetime = fields.Datetime('Old Value Datetime', store=True)
    ov_final = fields.Char('Old Value', compute='_compute_final_value', store=True)

    old_value = fields.Char('Old Value', store=True)
    new_value = fields.Char('New Value', store=True)

    # New values
    nv_integer = fields.Integer('New Value Integer', store=True)
    nv_float = fields.Float('New Value Float', store=True)
    nv_char = fields.Char('New Value Char', store=True)
    nv_text = fields.Text('New Value Text', store=True)
    nv_date = fields.Date('New Value Date', store=True)
    nv_datetime = fields.Datetime('New Value Datetime', store=True)
    nv_final = fields.Char('New Value', compute='_compute_final_value', store=True)

    @api.depends('active')
    def _compute_user(self):
        for record in self:
            record.user_id = self.env.uid

    @api.depends('ov_final', 'nv_final')    
    def _compute_final_value(self):
        for record in self:
            if record.ov_integer != False or record.ov_integer != 0:
                record.ov_final = record.ov_integer                 
            if record.ov_float != False or record.ov_float != 0:
                record.ov_final = record.ov_float                      
            if record.ov_char != False or record.ov_char:
                record.ov_final = record.ov_char                      
            if record.ov_text != False:
                record.ov_final = record.ov_text                      
            if record.ov_date != False:
                record.ov_final = record.ov_date                      
            if record.ov_datetime != False:
                record.ov_final = record.ov_datetime
            if record.nv_integer != False or record.nv_integer != 0:
                record.nv_final = record.nv_integer                           
            if record.nv_float != False or record.nv_float != 0:
                record.nv_final = record.nv_float                           
            if record.nv_char != False:
                record.nv_final = record.nv_char                           
            if record.nv_text != False:
                record.nv_final = record.nv_text                           
            if record.nv_date != False:
                record.nv_final = record.nv_date                           
            if record.nv_datetime != False:
                record.nv_final = record.nv_datetime