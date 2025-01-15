# -*- coding: utf-8 -*-
##############################################################################
#
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).
# See LICENSE file for full copyright and licensing details.
#
##############################################################################

{
    'name': 'Aircall API Integration',
    'version': '18.0.1.1',
    'license': 'OPL-1',
    'summary': """
        Aircall | Telephony | VOIP | voip | Call Log | call log | Call Record|
        Call Track | call track | Incoming call | dial | direct dial from odoo |
        call management | call integration | call history |  VOIP call
    """,
    'category': 'Extra Tools',
    'description': """
        Aircall API Integration, it will sync contacts, call log activities
        and make click to dial and insight cards view.
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['web', 'contacts', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs_data.xml',
        'data/res_partner_demo.xml',
        'views/number_views.xml',
        'views/res_company_view.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'views/mail_message_view.xml',
        'views/aircall_details_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'cit_aircall_api_integration/static/src/js/aircallPhone.js',
            'cit_aircall_api_integration/static/src/js/aircall.js',
            'cit_aircall_api_integration/static/src/js/aircall_dial.js',
            'cit_aircall_api_integration/static/src/xml/aircall_phone_field.xml',
            ('include', 'cit_aircall_api_integration.assets_frontend'),

        ],
        'cit_aircall_api_integration.assets_frontend': [
            ('include', 'web._assets_helpers'),
            'cit_aircall_api_integration/static/src/xml/aircall_dial.xml',
        ],
    },
    'images': ['static/description/banner.gif'],
}
