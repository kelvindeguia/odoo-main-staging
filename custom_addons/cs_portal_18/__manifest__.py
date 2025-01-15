# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Client Services",
    "summary": """Client Services""",
    "version": "1.0.1",
    "sequence": 2,
    "sequence": -100,
    "license": "AGPL-3",
    "category": "Productivity",
    "author": "Joseph Patrick Vargas",
    "website": "",
    "depends": ["base", "mail", "web", "hr", "hr_recruitment", ],
    "data": [
        "data/cs_portal_data.xml",
        "data/hr_recruitment_data.xml",
        "security/cs_portal_security.xml",
        "security/hr_recruitment_security.xml",
        "security/ir.model.access.csv",
        "views/actions.xml",
        "views/menu.xml",
        "views/form_views.xml",
        "views/list_views.xml",
        "views/pivot_views.xml",
        "views/assets.xml",
    ],
    'assets': {
        "web.assets_backend": [
            # "cs_portal_18/static/src/js/health_status_widget.js",
            # "cs_portal_18/static/src/css/health_status_widget.css",
            # 'web/static/src/js/core.js',  # Core JavaScript
            # 'web/static/src/js/field_registry.js',  # Field registry
            # 'web/static/src/js/fields/basic_fields.js',  # Basic fields
        ],
    },
    "application": True,
    "auto_install": False,
    "installable": True,
}