# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Caret IT Solutions Pvt. Ltd. (Website: www.caretit.com).           #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name': "Aircall Integration With CRM",
    'version': '18.0.0.1',
    'license': 'OPL-1',
    'summary': """Aircall With CRM""",
    'category': 'CRM',
    'description': """
        Create a link in insights for air call crm
    """,
    'author': 'Caret IT Solutions Pvt. Ltd.',
    'website': 'https://www.caretit.com',
    'depends': ['crm', 'cit_aircall_api_integration'],
    'data': [
        'views/crm_lead_view.xml',
        'views/res_config_settings_view.xml',
    ],
    'images': ['static/description/banner.jpg'],
}
