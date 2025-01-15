# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import pytz
from odoo import fields, models


_tzs = [(tz, tz) for tz in sorted(
    pytz.all_timezones, key=lambda tz: tz if not tz.startswith('Etc/') else '_')]

def _tz_get(self):
    return _tzs


class Number(models.Model):
    _name = 'number.number'
    _description = 'Numbers'

    number_id = fields.Char(string='Phone ID')
    name = fields.Char(string='Name', required=True)
    direct_link = fields.Char(string='Direct Link')
    digits = fields.Char(string='Digits')
    country = fields.Char(string='Country')
    tz = fields.Selection(
        _tz_get, string='Timezone', default=lambda self: self._context.get('tz'))
    open_status = fields.Boolean(string='Open')
    availability_status = fields.Selection(
        [('open', 'Open'), ('custom', 'Custom'), ('closed', 'Closed')],
        string='Availability Status')
    priority = fields.Selection(
        [('null', 'Null'), ('0', '0'), ('1', '1')],
        string='Availability Status', default='null')
    is_ivr = fields.Boolean(string='Is IVR?')
    live_recording_activated = fields.Boolean(string='Live Recording Activated?')
