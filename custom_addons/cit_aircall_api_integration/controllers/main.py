# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

import logging
from odoo import http

_logger = logging.getLogger(__name__)


class AircallIntegration(http.Controller):

    @http.route('/aircall/webhook', auth='public', methods=['POST'], type='json', csrf=False)
    def webhook_listener(self, **kw):
        """ we can use this to retrieve json payload directly instead of json-rpc formatted json """
        json_payload = dict(http.request.dispatcher.jsonrequest)
        if "token" not in json_payload:
            _logger.warning("Received malformed json payload at webhook endpoint from {}".format(
                http.request.httprequest.environ['REMOTE_ADDR']))
            return
        authentificated = http.request.env["aircall.webhook"].validate_webhook_token(
            json_payload["token"])
        if not authentificated:
            _logger.warning("Could not authentificate webhook call from {}".format(
                http.request.httprequest.environ["REMOTE_ADDR"]))
            return
        _logger.warning(json_payload)
        http.request.env["aircall.webhook"].register(json_payload)
        return
