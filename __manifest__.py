# -*- coding: utf-8 -*-
{
    'name': 'Sections and Machines API',
    'version': '18.0.1.0.0',
    'category': 'API',
    'summary': 'REST API for Sections and Machines Management',
    'description': """
Sections and Machines API Addon
================================

This addon provides REST API endpoints to manage sections and machines.

Features:
- Create, read, update, and delete sections
- Create, read, update, and delete machines
- Machines are linked to sections
- Manage section-machine relationships

Usage:
Sections:
- POST /api/sections/create - Create a new section
- GET /api/sections/list - List all active sections
- GET /api/sections/get/<id> - Get specific section
- PUT /api/sections/update/<id> - Update section
- DELETE /api/sections/delete/<id> - Delete section (soft delete)

Machines:
- POST /api/machines/create - Create a new machine (requires section_id)
- GET /api/machines/list - List all active machines
- GET /api/machines/get/<id> - Get specific machine
- GET /api/machines/by_section/<section_id> - Get machines by section
- PUT /api/machines/update/<id> - Update machine
- DELETE /api/machines/delete/<id> - Delete machine (soft delete)
    """,
    'author': 'Your Name',
    'website': 'https://www.odoo.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/section_views.xml',
        'views/machine_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

