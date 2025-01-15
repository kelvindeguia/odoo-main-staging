# -*- coding: utf-8 -*-

from odoo import fields, models

class Blacklist(models.Model):
    _name = "hr.blacklist"
    _description = "Blacklist"
    _order = "id desc"
    _rec_name = "name"

    active = fields.Boolean("Active", default=True,
                            help="If the active field is set to false, it will allow you to hide the case without removing it.")
    name = fields.Char('Blacklist Name', store=True)                
    email = fields.Char('Email', store=True)
