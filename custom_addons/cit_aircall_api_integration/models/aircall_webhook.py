# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

import logging
import time
from datetime import datetime

import phonenumbers
import requests
from markupsafe import Markup
from odoo.http import request

from odoo import api, models

_logger = logging.getLogger(__name__)

AIRCALL_API_URL = 'https://api.aircall.io/v1'


class AircallWebhook(models.TransientModel):
    _name = 'aircall.webhook'
    _description = 'Aircall Webhook'

    @api.model
    def validate_webhook_token(self, token):
        """ Method for validate the aircall webhook token. """
        true_token = self.env['ir.config_parameter'].sudo(
        ).get_param('cit_aircall_api_integration.default_aircall_integration_token')
        if true_token is False:
            _logger.warning(
                'Aircall integration token has not been set. Webhooks cannot work without it.')
        return true_token == token

    @api.model
    def get_aircall_api_config(self):
        """ Will throw an error if the config is not set """
        sudo_param = self.sudo().env['ir.config_parameter']
        return sudo_param.get_param(
            'cit_aircall_api_integration.default_api_id'), sudo_param.get_param(
            'cit_aircall_api_integration.default_api_token')

    @api.model
    def register(self, payload):
        """ Method where all webhook events are defined. """
        register_map = {
            'call.created': self._send_insight_card,
            'call.ended': self._register_call,
            # 'call.answered': self._register_call_answers,
            'call.commented': self._register_comment,
            'contact.created': self._register_contact,
        }
        try:
            method = register_map[payload['event']]
        except KeyError:
            _logger.warning(
                'An unimplemented webhook of type [{}] has been received. Uncheck it in aircall dashboard.'.format(
                    payload['event']))
            return
        method(payload)

    def create_call_detail(self, call_id, recording, waiting_time, i,
                           mail_data,
                           data, talk_time, tags, comments):

        # Check if the call detail already exists
        existing_call_detail = self.env['aircall.details'].sudo().search_read([
            ('aircall_call_id', '=', call_id)], fields=['aircall_call_id'])
        if existing_call_detail:
            # If a similar call detail already exists, do not create a duplicate
            return
        number = data['number']['digits'] if data.get('number') and data['number'].get('digits') else ''
        self.env['aircall.details'].sudo().create({
            'aircall_call_id': call_id,
            'call_by_user': data['number']['name'],
            'customer_id': i.id if i else False,
            'recording_url': recording,
            'phonenumbers': data['raw_digits'],
            'call_qualification': data["direction"],
            'call_duration': time.strftime(
                '%H:%M:%S', time.gmtime(data['duration'])),
            'waiting_time': waiting_time,
            'call_time': talk_time,
            'air_call_number': number,
            'tags': tags,
            'notes': comments and comments[0] or ''
        })

        if tags and i:
            # Prepare a list of sanitized tags
            tag_list = [tag.strip() for tag in tags if isinstance(tag, str) and tag.strip()]

            for tag in tag_list:
                # Fetch or create the partner category
                category = self.env['res.partner.category'].sudo().search([('name', '=', tag)],
                                                                          limit=1)
                if not category:
                    category = self.env['res.partner.category'].sudo().create({'name': tag})

                # Append the category to the category_id field
                i.sudo().write({'category_id': [(4, category.id)]})

            # Fetch configuration setting for Helpdesk tickets
            helpdesk_ticket = self.env['ir.config_parameter'].sudo().get_param(
                'cit_aircall_helpdesk.helpdesk_log_note_setting'
            )

            # Fetch or create CRM tags and append them to the last created CRM lead
            crm_tag_ids = []
            for tag in tag_list:
                tag_rec = self.env['crm.tag'].sudo().search([('name', '=', tag)], limit=1)
                if not tag_rec:
                    tag_rec = self.env['crm.tag'].sudo().create({'name': tag})
                crm_tag_ids.append(tag_rec.id)

            last_crm_lead = self.env['crm.lead'].sudo().search([], order='create_date desc',
                                                               limit=1)
            if last_crm_lead:
                for tag_id in crm_tag_ids:
                    last_crm_lead.sudo().write({'tag_ids': [(4, tag_id)]})  # Append tags
                last_crm_lead._cr.commit()

            # Logic for Helpdesk tickets
            if helpdesk_ticket == 'open_new_ticket':
                helpdesk_tag_ids = []
                for tag in tag_list:
                    tag_rec = self.env['helpdesk.tag'].sudo().search([('name', '=', tag)],
                                                                     limit=1)
                    if not tag_rec:
                        tag_rec = self.env['helpdesk.tag'].sudo().create({'name': tag})
                    helpdesk_tag_ids.append(tag_rec.id)

                last_helpdesk_ticket = self.env['helpdesk.ticket'].sudo().search([],
                                                                                 order='create_date desc',
                                                                                 limit=1)
                if last_helpdesk_ticket:
                    for tag_id in helpdesk_tag_ids:
                        last_helpdesk_ticket.sudo().write(
                            {'tag_ids': [(4, tag_id)]})  # Append tags
                    last_helpdesk_ticket._cr.commit()

            elif helpdesk_ticket == 'add_log_note_exciting':
                tickets_with_log_note = self.env['helpdesk.ticket'].sudo().search(
                    [('add_log_note', '=', True)]
                )
                if tickets_with_log_note:
                    helpdesk_tag_ids = []
                    for tag in tag_list:
                        tag_rec = self.env['helpdesk.tag'].sudo().search([('name', '=', tag)],
                                                                         limit=1)
                        if not tag_rec:
                            tag_rec = self.env['helpdesk.tag'].sudo().create({'name': tag})
                        helpdesk_tag_ids.append(tag_rec.id)

                    for ticket in tickets_with_log_note:
                        for tag_id in helpdesk_tag_ids:
                            ticket.sudo().write({'tag_ids': [(4, tag_id)]})  # Append tags
                    self._cr.commit()

    @api.model
    def _register_comment(self, payload):
        """Method called when notes being noted to the call."""
        comments = []
        data = payload.get('data')
        for comment in data.get('comments'):
            comments.append('\n{}'.format(comment.get('content')))
        call_comment = "\n".join(comments)
        aircall_detail_rec = self.env['aircall.details'].sudo().search([
            ('aircall_call_id', '=', data.get('id'))], order='id desc', limit=1)
        if aircall_detail_rec:
            if call_comment and not aircall_detail_rec.notes:
                _logger.info('\n\nAircallDetailRec-Comment ::::::::::%s', aircall_detail_rec,
                             aircall_detail_rec.notes)
                aircall_detail_rec.sudo().write({'notes': call_comment})

    def _process_comments_tags(self, data):
        """This method gives Comments and Tags which is added During the call"""
        comments = [f"\n{comment['content']}" for comment in data['comments']]
        tags = [f"\n{tag['name']}" for tag in data['tags']]
        return comments, tags

    def _process_call_with_conf_num(self, payload, comments, tags):
        """This method allows user to add the logout which is configured in setting."""
        data = payload['data']
        partner_obj = self.env['res.partner'].sudo()
        external_entity_id = self._find_partner(partner_obj, data['raw_digits'])
        check_msg = self.env['mail.message'].sudo().search_read([('aircall_call_id', '=', data['id'])], limit=1)
        if not check_msg and payload.get('event') == 'call.ended':
            if not external_entity_id:
                external_entity_id = self._handle_unknown_contact_creation(external_entity_id, partner_obj, data)
            for partner in external_entity_id:
                if partner.add_log_note:
                    talk_time, waiting_time = self._calculate_times(data)
                    message = self._generate_message(data, talk_time, waiting_time, tags, comments)
                    self._post_message_and_create_call(partner, message, data, talk_time, waiting_time, tags, comments)
                    partner.update({'add_log_note': False})

    def _process_call_without_conf_num(self, data):
        """This method calls when call is disconnected."""
        partner_obj = self.env['res.partner']
        external_entity_ids = self._find_partner(partner_obj, data['raw_digits']).filtered(lambda a: a.add_log_note)
        if external_entity_ids:
            [external_entity_id.update({'add_log_note': False}) for external_entity_id in external_entity_ids]

    @api.model
    def _register_call(self, payload):
        """ Method called when the call event is performed. """
        _logger.info(payload)
        assert payload['resource'] == 'call'

        data = payload['data']
        company = request.env.company
        number = data['number']
        # Common data processing
        conf_num = self._get_conf_num(company, number)
        comments, tags = self._process_comments_tags(data)
        if conf_num:
            self._process_call_with_conf_num(payload, comments, tags)
        else:
            self._process_call_without_conf_num(data)

    def _get_conf_num(self, company, number):
        """Fetches configuration numbers based on the company's number config."""
        if not company.number_config_ids:
            return []
        num_search = self.env['number.number'].sudo().search(
            [('id', 'in', company.number_config_ids.ids)]
        )
        conf_num = [num for num in num_search if
                    str(num.number_id) == str(number['id']) and str(num.digits) == str(number['digits'])]
        return conf_num

    def _find_partner(self, partner_obj, raw_digits):
        """Finds the external entity based on the phone or mobile number."""
        return partner_obj.sudo().search(
            [
                '|', ('phone', 'ilike', raw_digits), '|', ('phone', 'ilike', raw_digits.replace(" ", "")), '|',
                ('mobile', 'ilike', raw_digits),
                ('mobile', 'ilike', raw_digits.replace(" ", ""))],order='id desc',limit=1
        )

    def _handle_unknown_contact_creation(self, external_entity_id, partner_obj, data):
        """Handles the creation of unknown contacts if allowed."""
        create_aircall_contact = self.env['ir.config_parameter'].sudo().get_param(
            'cit_aircall_api_integration.allow_create_unknown_contacts'
        )

        if create_aircall_contact and not external_entity_id:
            aircall_contact_find = self._find_partner(partner_obj, data['raw_digits'])
            if not aircall_contact_find:
                external_entity_id = partner_obj.sudo().create({
                    'name': "NEW : " + data['raw_digits'],
                    'phone': data['raw_digits'],
                    'email': '',
                })

        for partner in external_entity_id:
            if len(external_entity_id) == 1 and not partner.add_log_note:
                partner.add_log_note = True

        return external_entity_id

    def _calculate_times(self, data):
        """Calculates the talk time and waiting time based on call data."""
        talk_time = waiting_time = 0
        if data['answered_at']:
            talk_time = time.strftime('%H:%M:%S', time.gmtime(data['ended_at'] - data['answered_at']))
            waiting_time = time.strftime('%H:%M:%S', time.gmtime(data['answered_at'] - data['started_at']))

        return talk_time, waiting_time

    def _generate_message(self, data, talk_time, waiting_time, tags, comments):
        """Generates the message to be logged or sent."""
        started_at = datetime.fromtimestamp(int(data['started_at'])).strftime(
            '%A %b %d %Y (%I:%M:%S %p)')
        ended_at = datetime.fromtimestamp(int(data['ended_at'])).strftime(
            '%A %b %d %Y (%I:%M:%S %p)')

        missed_call_status = 'No' if data['answered_at'] else 'Yes'
        return Markup(
            """
                                    <strong>Call ID:</strong> %(Call ID)s<br/>
                                    <strong>Started At:</strong> %(Start At)s<br/>
                                    <strong>Ended At:</strong> %(End At)s<br/>
                                    <strong>Contact Number:</strong> %(Contact Number)s<br/>
                                    <strong>Call direction:</strong> %(Call direction)s<br/>
                                    <strong>Aircall User:</strong> %(Aircall User)s<br/>
                                    <strong>Aircall Number:</strong> %(Aircall Number)s<br/>
                                    <strong>Call Duration:</strong> %(Call Duration)s<br/>
                                     <strong>Missed Call:</strong> %(Missed Call)s<br/>
                                    <strong>Tags:</strong> %(Tags)s<br/>
                                    <strong>Comments:</strong> %(Comments)s<br/>
                                    """
            
            ) % {
            'Call ID': '{}'.format(data["id"]),
            'Start At': '{}'.format(started_at),
            'End At': '{}'.format(ended_at),
            'Contact Number':'{}'.format(data["raw_digits"]),
            'Call direction': data["direction"],
            'Call Duration': '{} Sec'.format(data['duration']),
            'Missed Call': '{}'.format(missed_call_status),
            'Tags': '{}'.format(", ".join(tags)),
            'Comments':'{}'.format(" ".join(comments)),
            'Aircall User': '{}'.format(data["user"]["name"]),
            'Aircall Number': '{}'.format(data["number"]["name"]),

        }

    def _post_message_and_create_call(self, partner, message, data, talk_time, waiting_time,
                                      tags, comments):
        """Posts a message and creates the call detail entry."""
        author_ref = self.env.ref('cit_aircall_api_integration.aircall_res_partner_1',
                                  raise_if_not_found=False)
        author_id = author_ref.id if author_ref else None

        mail_data = partner.sudo().message_post(
            body=message,
            author_id=author_id if author_id else None
        )
        if mail_data:
            mail_data.aircall_call_id = data['id']
            partner.sudo().write({'add_log_note': False})
            self.create_call_detail(
                data['id'], data['asset'], waiting_time, partner, mail_data, data, talk_time,
                tags, comments
            )

    @api.model
    def _send_insight_card(self, payload):
        """ Method for sending the insight card """
        api_id, api_token = self.get_aircall_api_config()
        if False in [api_id, api_token]:
            _logger.warning(
                "Aircall api credentials are not set. Some features won't work")
            return
        json_field = self._populate_insight_card(payload)
        if json_field is False:
            # Callee was not found on the system on the system
            return
        aircall_url = AIRCALL_API_URL + "/calls/" + \
                      str(payload['data']['id']) + "/insight_cards"
        requests.post(aircall_url, auth=(
            api_id, api_token), json=json_field)

    @api.model
    def _populate_insight_card(self, payload):
        """ Method for populating the insight card to the current call. """
        data = payload['data']
        partner = self.env['res.partner'].sudo().search(
            [
                '|', ('phone', 'ilike', data['raw_digits']), '|',
                ('phone', 'ilike', data['raw_digits'].replace(" ", "")), '|',
                ('mobile', 'ilike', data['raw_digits']),
                ('mobile', 'ilike', data['raw_digits'].replace(" ", ""))])
        partner_name_string = 'Select Contact'

        if len(partner) == 1:
            partner_name_string = partner.name
            partner.write({'add_log_note': True})
        if data.get('direction') == 'inbound':
            partner = self._handle_unknown_contact_creation(partner, self.env['res.partner'], data)
            partner_name_string = partner.name

        json_field = self._generate_insight_card_json(partner, partner_name_string, data)

        if json_field:
            return json_field
        else:
            return False

    def _generate_insight_card_json(self, partner, partner_name_string, data):
        """ Generate JSON field for insight card. """
        partner_open = self.sudo().env.ref('cit_aircall_api_integration.action_contacts_extended')
        partner_open.update(
            {'domain': [
                '|', ('phone', 'ilike', data['raw_digits']), '|',
                ('phone', 'ilike', data['raw_digits'].replace(" ", "")), '|',
                ('mobile', 'ilike', data['raw_digits']),
                ('mobile', 'ilike', data['raw_digits'].replace(" ", ""))]})

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + \
                   '/web?=#action=%s&model=crm.lead&view_type=list&cids=1' % partner_open.id

        return {'contents': [
            {
                'type': 'title',
                'text': 'Odoo information',
                'link': base_url,
            },
            {
                'type': 'shortText',
                'label': 'Contact',
                'text': partner_name_string,
                'link': base_url
            }
        ]}

    @api.model
    def _register_contact(self, payload):
        """ Method called when contact is created in aircall. """
        _logger.info(payload)
        phone_format = ''
        res_partner = self.env['res.partner']
        phone_details = self.env['phone.details']
        email_details = self.env['email.details']
        contact = payload['data']
        company = False
        if contact['phone_numbers']:
            phone = phonenumbers.parse(contact['phone_numbers'][0]['value'])
            phone_format = phonenumbers.format_number(
                phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        partner = res_partner.sudo().search([
            ('name', '=', contact['first_name']),
                '|', ('phone', 'ilike', phone_format), ('phone', 'ilike', phone_format.replace(" ", ""))
        ])
        if not partner:
            if contact['company_name']:
                company = res_partner.sudo().search(
                    [('name', '=', contact['company_name'])], limit=1)
                if not company:
                    company = res_partner.sudo().create({
                        'name': contact['company_name'],
                        'company_type': 'company',
                        'is_company': True,
                        'aircall_id': contact['id']
                    })
            partner = res_partner.sudo().create({
                'name': contact['first_name'],
                'last_name': contact['last_name'] or '',
                'comment': contact['information'],
                'phone': phone_format if contact['phone_numbers'] else '',
                'email': contact['emails'][0]['value'] if contact['emails'] else '',
                'parent_id': company and company.id or False,
                'aircall_id': contact['id'],
                'direct_link': contact['direct_link'],
                'is_shared': contact['is_shared'],
            })
            for phone in contact['phone_numbers']:
                phone_details.sudo().create({
                    'phone_id': phone['id'],
                    'label': phone['label'],
                    'value': phone['value'],
                    'partner_id': partner.id,
                })
            for email in contact['emails']:
                email_details.sudo().create({
                    'email_id': email['id'],
                    'label': email['label'],
                    'value': email['value'],
                    'partner_id': partner.id,
                })
