# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo.addons.cit_aircall_api_integration.models.authorization import AuthorizeAircallApi
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    number_crm_config_ids = fields.Many2many(
        'number.number',
        relation='config_crm_rel',
        column1='config_id',
        column2='crm_id',
        string='CRM Config'
    )

    @api.model
    def get_values(self):
        values = super(ResConfigSettingsInherit, self).get_values()
        if not self.env.company.number_crm_config_ids:
            values['number_crm_config_ids'] = False
        else:
            values['number_crm_config_ids'] = [
                (6, 0, self.env.company.number_crm_config_ids.ids)]
        return values

    def set_values(self):
        values = super(ResConfigSettingsInherit, self).set_values()
        self.env.company.write(
            {'number_crm_config_ids': [(6, 0, self.number_crm_config_ids.ids)]})
        return values

    def fetch_crm_numbers(self):
        """ Method for fetch numbers from aircall to odoo. """
        auth, url, api_id, api_token = self.get_aircall_auth()
        NumObj = self.env['number.number']
        num_list = []
        if auth and auth.json():
            numbers = AuthorizeAircallApi(url, api_id, api_token).get_numbers()
            count = 0
            for number_data in numbers:
                for number in number_data.json()['numbers']:
                    count = count + 1
                    exist_num = NumObj.search([
                        ('number_id', '=', number['id']),
                        ('digits', '=', number['digits'])])
                    if not exist_num:
                        num_list.append(self.create_update_number(NumObj, number, 'create').id)
                    else:
                        self.create_update_number(exist_num, number, 'write')
                        num_list.append(exist_num.id)
                    if num_list:
                        self.company_id.write(
                            {'number_crm_config_ids': [(6, 0, num_list)],
                             'number_config_ids': [(6, 0, num_list)]})

        elif auth.json() and auth.json().get('error'):
            raise ValidationError(_('Please %s', (auth.json().get('troubleshoot'))))