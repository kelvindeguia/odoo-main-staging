# -*- coding: utf-8 -*-

from odoo import fields, models

class CandidateForm(models.Model):
    _name = "hr.candidate.form"
    _description = "Candidate Form"
    _order = "id desc"
    _rec_name = "name"

    active = fields.Boolean(string="Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    name = fields.Char(string='Candidate Name', store=True)                
    email = fields.Char(string='Candidate Email', store=True)
    residing_metro_manila = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Are you currently residing within Metro Manila?', store=True)
    relocate = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='If not residing in Metro Manila, are you willing to relocate to Metro Manila for this position?', store=True)
    specification_ids = fields.Many2many('hr.appointments.specification', string='Do you have any specific or obligatory appointments in the next twelve (12) months? Please check all that apply:', store=True)
    appointments_specification = fields.Text('If you ticked any of the first five items, please specify details:', store=True)
    diagnosed = fields.Text(string='Have you been previously diagnosed with or treated for any medical condition, which, if left untreated, may adversely affect your ability to perform the duties and responsibilities attendant to the position for which you are applying? If so, please specify.', store=True)
    medical_condition = fields.Text(string='Do you presently have any medical condition, physical injury, impairment, or disability that may in any manner adversely affect your ability to adequately and satisfactorily perform the duties and responsibilities attendant to the position for which you are applying? If so, please specify.', store=True)
    combined = fields.Boolean(string='Combined', store=True)