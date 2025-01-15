# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError
from odoo import fields, models, api

try:
    import phonenumbers
except Exception as e:
    _logger.error(f"Import error: %s {e}")
    raise ValidationError("phonenumbers Import error")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phone = fields.Char(unaccent=False, copy=False)
    email = fields.Char(copy=False)
    synced_to_aircall = fields.Boolean(string='Synced to Aircall', copy=False)
    last_name = fields.Char(string='Last Name')
    aircall_id = fields.Char(string='Aircall ID', copy=False)
    direct_link = fields.Char(string='Direct Link', copy=False)
    is_shared = fields.Boolean(string='Is Shared', copy=False)
    is_log_send = fields.Boolean(string='Is Log Send', copy=False)
    updated_contact = fields.Boolean(string='Updated Contact', copy=False)
    phone_details_ids = fields.One2many(
        'phone.details', 'partner_id', string='Phone Details',
        copy=False, help="Phone Number Details When new contact create for Aircall")
    email_details_ids = fields.One2many(
        'email.details', 'partner_id', string='Email Details',
        copy=False, help="New Email ID when new contact create for Aircall")
    aircall_detail_ids = fields.One2many(
        'aircall.details', 'customer_id', string='Air Call')
    add_log_note = fields.Boolean(string="Add Log Note", default=False)

    def write(self, vals):
        """Write method to set the phone and mobile numbers in a valid format."""
        if any(field in vals for field in ['name', 'phone', 'email', 'mobile']):
            vals['updated_contact'] = False
        # Format phone number if provided
        if 'phone' in vals and vals['phone']:
            vals['phone'] = self._format_phone_number(vals['phone'])
        # Format mobile number if provided
        if 'mobile' in vals and vals['mobile']:
            vals['mobile'] = self._format_phone_number(vals['mobile'])
        return super(ResPartner, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Create method to set the phone and mobile numbers in a valid format."""
        for vals in vals_list:
            if 'phone' in vals and vals['phone']:
                vals['phone'] = self._format_phone_number(vals['phone'])
            if 'mobile' in vals and vals['mobile']:
                vals['mobile'] = self._format_phone_number(vals['mobile'])
        return super(ResPartner, self).create(vals_list)

    def _format_phone_number(self, number):
        """Helper method to format the phone number to international format."""
        try:
            return phonenumbers.format_number(
                phonenumbers.parse(number),
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        except phonenumbers.NumberParseException:
            raise ValidationError("Phone number must have correct value, country code, or region.")
        except Exception as e:
            _logger.error(f"Error formatting phone number: {e}")
            raise ValidationError("An unexpected error occurred while formatting the phone number.")
