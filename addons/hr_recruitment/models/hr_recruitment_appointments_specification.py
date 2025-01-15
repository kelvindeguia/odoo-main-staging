# -*- coding: utf-8 -*-

from odoo import fields, models

class AppointmentsSpecification(models.Model):
    _name = "hr.appointments.specification"
    _description = "Appointments Specification"
    _rec_name = "name"

    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    name = fields.Char('Name', store=True)    
    sequence = fields.Integer('Sequence', store=True)
