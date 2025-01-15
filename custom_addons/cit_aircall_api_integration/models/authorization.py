# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import base64
import logging
import math

import requests
from odoo.exceptions import ValidationError

from odoo import _

_logger = logging.getLogger(__name__)


class AuthorizeAircallApi():
    """Main conversation handeling with Aircall API v1."""

    def __init__(self, url, api_id, api_token):
        """Construction Connection and setup."""
        self.api_url = url
        self.api_id = api_id
        self.api_token = api_token

    def get_authentication(self):
        """ Method for authentication. """
        headers = {'Authorization': 'Basic %s' % base64.b64encode(bytes(
            '%s:%s' % (self.api_id, self.api_token), encoding='utf8')).decode('ascii')}
        try:
            return requests.request('GET', self.api_url + '/v1/ping', headers=headers)
        except:
            raise ValidationError(_('Please Check Configuration !!'))

    def post_contacts(self, values):
        """ Method for post contacts """
        return requests.post(self.api_url + '/v1/contacts', auth=(
            self.api_id, self.api_token), json=values)

    def get_numbers(self):
        """ Method for get numbers """
        vals = []
        url = self.api_url + '/v1/numbers?per_page=%s' % (50)
        userPass = base64.b64encode(
            bytes("%s:%s" % (self.api_id, self.api_token), encoding='utf8')).decode(
            "ascii")
        headers = {"Authorization": "Basic %s" % userPass}
        response = requests.request("GET", url, headers=headers)
        if response and response.json:
            count = math.ceil(response.json()['meta']['total'] / 50) + 1
            if count == 1:
                count += 1
            for i in range(1, count):
                url = self.api_url + '/v1/numbers?page=%s&per_page=%s' % (i, 50)
                response = requests.request("GET", url, headers=headers)
                vals.append(response)
        return vals
