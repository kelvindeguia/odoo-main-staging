# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

import logging
import time

from odoo import api, models

_logger = logging.getLogger(__name__)


class AircallWebhook(models.TransientModel):
    _inherit = 'aircall.webhook'
    _description = 'Air call CRM'

    def _populate_insight_card(self, payload):
        result = super()._populate_insight_card(payload)
        data = payload['data']
        if not result:
            return False
        # Custom logic for CRM leads
        lead = self._get_crm_lead(data['raw_digits'])
        leads_text = 'Select Opportunity'
        partner = self._find_partner(self.env['res.partner'], data['raw_digits'])
        if len(lead) <= 1:
            leads_text = partner[0].name + "'s Opportunity"
        result = self._extend_card_with_lead_info(result, lead, leads_text, partner)
        return result

    def _get_crm_lead(self, raw_digits):
        """ Fetch CRM lead by phone or mobile number. """
        return self.env['crm.lead'].sudo().search([
            '|', ('phone', 'ilike', raw_digits), '|', ('phone', 'ilike', raw_digits.replace(" ", "")), '|', ('mobile', 'ilike', raw_digits),
        ('mobile', 'ilike', raw_digits.replace(" ", ""))])

    def _extend_card_with_lead_info(self, result, lead, leads_text, partner):
        """ Extend insight card with lead information. """
        base_url = self.env['ir.config_parameter'].sudo(
        ).get_param('web.base.url')
        action_id = self.sudo().env.ref('cit_aircall_crm.crm_lead_opportunities_extended')
        action_id.write({'context': {
            'default_partner_id': partner.id, 'default_name': 'Opportunity of ' + partner.name}})
        if lead:
            action_id.write({'domain': [('id', 'in', lead.ids)]})
            base_url += '/web?=#action=%s&model=crm.lead&view_type=list&cids=1' % action_id.id
        else:
            action_id.write({'domain': [('id', '=', False)]})
            base_url += '/web?=#action=%s&model=crm.lead&view_type=list&cids=1' % action_id.id
        result['contents'].append({
            'type': 'shortText',
            'label': 'Opportunity',
            'text': leads_text,
            'link': base_url
        })
        _logger.info(result)
        return result

    @api.model
    def _register_call(self, payload):
        res = super()._register_call(payload)
        data = payload['data']
        comments, tags = self._process_comments_tags(data)
        crm_lead = self.env['crm.lead'].sudo().search(
            ['|', ('phone', 'ilike', data['raw_digits']),
             ('mobile', 'ilike', data['raw_digits']),
             ('add_log_note', '=', True)])
        if not data['answered_at']:
            data['answered_at'] = data['ended_at']
        self._process_leads(crm_lead, data, tags, comments)
        return res

    def _process_leads(self, crm_lead, data, tags, comments):
        """This method calls for adding a log note in lead for configured aircall user"""
        for lead in crm_lead:
            talk_time, waiting_time = self._calculate_times(data)
            if self._is_number_configured(data['number']['digits']):
                message = self._generate_message(data, talk_time, waiting_time, tags, comments)
                author_ref = self.env.ref('cit_aircall_api_integration.aircall_res_partner_1',
                                          raise_if_not_found=False)
                author_id = author_ref.id if author_ref else None
                mail_data = lead.sudo().message_post(body=message, author_id=author_id if author_id else None)
                if mail_data:
                    mail_data.aircall_call_id = data['id']
                    self.create_call_detail(
                        data['id'], data['asset'], waiting_time, lead, mail_data, data, talk_time,
                        tags, comments)
        crm_lead.filtered(lambda a: a.add_log_note).sudo().write({'add_log_note': False})

    def _is_number_configured(self, digits):
        """Find the configure aircall number in setting"""
        return self.env.company.number_crm_config_ids.sudo().filtered(lambda num: num.digits == digits)
