# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request, Response
import json
import logging

_logger = logging.getLogger(__name__)

class SectionsMachinesAPI(http.Controller):

    def _cors_headers(self):
        """CORS headers to allow Flutter Web app to access the API"""
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
    
    def _json_response(self, data, status=200):
        """Return JSON response with CORS headers"""
        return Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=status,
            headers=self._cors_headers()
        )

    # ==================== SECTIONS API ====================

    @http.route('/api/sections/create', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def create_section(self, **kw):
        """Create a new section"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            # Get request data
            raw_body = request.httprequest.data
            if not raw_body:
                raw_body = request.httprequest.get_data()
            
            if not raw_body:
                return self._json_response({
                    'success': False,
                    'message': 'Request body must be JSON'
                }, status=400)
            
            # Decode bytes to string
            if isinstance(raw_body, bytes):
                raw_body = raw_body.decode('utf-8')
            
            # Parse JSON
            try:
                data = json.loads(raw_body)
            except json.JSONDecodeError as e:
                _logger.error(f"JSON decode error: {e}, raw_body: {raw_body}")
                return self._json_response({
                    'success': False,
                    'message': f'Invalid JSON format: {str(e)}'
                }, status=400)
            
            # Get params (support both formats)
            params = data.get('params', data)
            
            _logger.info(f"Creating section with params: {params}")
            
            # Validate required fields
            if not params.get('name'):
                return self._json_response({
                    'success': False,
                    'message': 'name is required'
                }, status=400)
            
            if not params.get('section_id'):
                return self._json_response({
                    'success': False,
                    'message': 'section_id is required'
                }, status=400)
            
            if not params.get('location'):
                return self._json_response({
                    'success': False,
                    'message': 'location is required'
                }, status=400)
            
            # Create section
            section = request.env['kiosk.section'].sudo().create({
                'name': params.get('name'),
                'section_id': params.get('section_id'),
                'location': params.get('location'),
            })
            
            _logger.info(f"Section created successfully with ID: {section.id}")
            
            return self._json_response({
                'success': True,
                'message': 'Section created successfully',
                'section': self._section_to_dict(section)
            })
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            _logger.error(f"Error creating section: {str(e)}\n{error_trace}")
            return self._json_response({
                'success': False,
                'message': str(e),
                'error_type': type(e).__name__
            }, status=500)

    @http.route('/api/sections/list', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False)
    def list_sections(self, **kw):
        """List all active sections"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            sections = request.env['kiosk.section'].sudo().search([('active', '=', True)])
            sections_list = [self._section_to_dict(s) for s in sections]
            
            return self._json_response({
                'success': True,
                'sections': sections_list
            })
        except Exception as e:
            _logger.error(f"Error listing sections: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/sections/get/<int:section_id>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False)
    def get_section(self, section_id, **kw):
        """Get specific section by ID"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            section = request.env['kiosk.section'].sudo().browse(section_id)
            if not section.exists() or not section.active:
                return self._json_response({
                    'success': False,
                    'message': 'Section not found'
                }, status=404)
            
            return self._json_response({
                'success': True,
                'section': self._section_to_dict(section)
            })
        except Exception as e:
            _logger.error(f"Error getting section: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/sections/update/<int:section_id>', type='http', auth='public', methods=['PUT', 'OPTIONS'], csrf=False)
    def update_section(self, section_id, **kw):
        """Update a section"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            raw_body = request.httprequest.data or request.httprequest.get_data()
            if isinstance(raw_body, bytes):
                raw_body = raw_body.decode('utf-8')
            
            if not raw_body:
                return self._json_response({
                    'success': False,
                    'message': 'Request body must be JSON'
                }, status=400)
            
            data = json.loads(raw_body)
            params = data.get('params', data)
            
            section = request.env['kiosk.section'].sudo().browse(section_id)
            
            if not section.exists() or not section.active:
                return self._json_response({
                    'success': False,
                    'message': 'Section not found'
                }, status=404)
            
            update_vals = {}
            if 'name' in params:
                update_vals['name'] = params.get('name')
            if 'section_id' in params:
                update_vals['section_id'] = params.get('section_id')
            if 'location' in params:
                update_vals['location'] = params.get('location')
            
            section.write(update_vals)
            
            return self._json_response({
                'success': True,
                'message': 'Section updated successfully',
                'section': self._section_to_dict(section)
            })
        except Exception as e:
            _logger.error(f"Error updating section: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/sections/delete/<int:section_id>', type='http', auth='public', methods=['DELETE', 'OPTIONS'], csrf=False)
    def delete_section(self, section_id, **kw):
        """Delete a section (soft delete)"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            section = request.env['kiosk.section'].sudo().browse(section_id)
            if not section.exists():
                return self._json_response({
                    'success': False,
                    'message': 'Section not found'
                }, status=404)
            
            section.write({'active': False})  # Soft delete
            
            return self._json_response({
                'success': True,
                'message': 'Section deleted successfully'
            })
        except Exception as e:
            _logger.error(f"Error deleting section: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    # ==================== MACHINES API ====================

    @http.route('/api/machines/create', type='http', auth='public', methods=['POST', 'OPTIONS'], csrf=False)
    def create_machine(self, **kw):
        """Create a new machine (requires section_id)"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            raw_body = request.httprequest.data or request.httprequest.get_data()
            if isinstance(raw_body, bytes):
                raw_body = raw_body.decode('utf-8')
            
            if not raw_body:
                return self._json_response({
                    'success': False,
                    'message': 'Request body must be JSON'
                }, status=400)
            
            data = json.loads(raw_body)
            params = data.get('params', data)
            
            section_id = params.get('section_id')
            if not section_id:
                return self._json_response({
                    'success': False,
                    'message': 'section_id is required'
                }, status=400)
            
            # Check if section exists
            section = request.env['kiosk.section'].sudo().browse(int(section_id))
            if not section.exists() or not section.active:
                return self._json_response({
                    'success': False,
                    'message': 'Section not found'
                }, status=404)
            
            _logger.info(f"Creating machine: {params}")
            
            machine = request.env['section.machine'].sudo().create({
                'name': params.get('name'),
                'section_id': int(section_id),
            })
            
            return self._json_response({
                'success': True,
                'message': 'Machine created successfully',
                'machine': self._machine_to_dict(machine)
            })
        except Exception as e:
            _logger.error(f"Error creating machine: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/machines/list', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False)
    def list_machines(self, **kw):
        """List all active machines"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            machines = request.env['section.machine'].sudo().search([('active', '=', True)])
            machines_list = [self._machine_to_dict(m) for m in machines]
            
            return self._json_response({
                'success': True,
                'machines': machines_list
            })
        except Exception as e:
            _logger.error(f"Error listing machines: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/machines/get/<int:machine_id>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False)
    def get_machine(self, machine_id, **kw):
        """Get specific machine by ID"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            machine = request.env['section.machine'].sudo().browse(machine_id)
            if not machine.exists() or not machine.active:
                return self._json_response({
                    'success': False,
                    'message': 'Machine not found'
                }, status=404)
            
            return self._json_response({
                'success': True,
                'machine': self._machine_to_dict(machine)
            })
        except Exception as e:
            _logger.error(f"Error getting machine: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/machines/by_section/<int:section_id>', type='http', auth='public', methods=['GET', 'OPTIONS'], csrf=False)
    def get_machines_by_section(self, section_id, **kw):
        """Get all machines for a specific section"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            section = request.env['kiosk.section'].sudo().browse(section_id)
            if not section.exists() or not section.active:
                return self._json_response({
                    'success': False,
                    'message': 'Section not found'
                }, status=404)
            
            machines = request.env['section.machine'].sudo().search([
                ('section_id', '=', section_id),
                ('active', '=', True)
            ])
            machines_list = [self._machine_to_dict(m) for m in machines]
            
            return self._json_response({
                'success': True,
                'section': self._section_to_dict(section),
                'machines': machines_list
            })
        except Exception as e:
            _logger.error(f"Error getting machines by section: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/machines/update/<int:machine_id>', type='http', auth='public', methods=['PUT', 'OPTIONS'], csrf=False)
    def update_machine(self, machine_id, **kw):
        """Update a machine"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            raw_body = request.httprequest.data or request.httprequest.get_data()
            if isinstance(raw_body, bytes):
                raw_body = raw_body.decode('utf-8')
            
            if not raw_body:
                return self._json_response({
                    'success': False,
                    'message': 'Request body must be JSON'
                }, status=400)
            
            data = json.loads(raw_body)
            params = data.get('params', data)
            
            machine = request.env['section.machine'].sudo().browse(machine_id)
            
            if not machine.exists() or not machine.active:
                return self._json_response({
                    'success': False,
                    'message': 'Machine not found'
                }, status=404)
            
            update_vals = {}
            if 'name' in params:
                update_vals['name'] = params.get('name')
            if 'section_id' in params:
                section_id = params.get('section_id')
                # Check if section exists
                section = request.env['kiosk.section'].sudo().browse(int(section_id))
                if not section.exists() or not section.active:
                    return self._json_response({
                        'success': False,
                        'message': 'Section not found'
                    }, status=404)
                update_vals['section_id'] = int(section_id)
            
            machine.write(update_vals)
            
            return self._json_response({
                'success': True,
                'message': 'Machine updated successfully',
                'machine': self._machine_to_dict(machine)
            })
        except Exception as e:
            _logger.error(f"Error updating machine: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    @http.route('/api/machines/delete/<int:machine_id>', type='http', auth='public', methods=['DELETE', 'OPTIONS'], csrf=False)
    def delete_machine(self, machine_id, **kw):
        """Delete a machine (soft delete)"""
        if request.httprequest.method == 'OPTIONS':
            return Response(status=200, headers=self._cors_headers())
        
        try:
            machine = request.env['section.machine'].sudo().browse(machine_id)
            if not machine.exists():
                return self._json_response({
                    'success': False,
                    'message': 'Machine not found'
                }, status=404)
            
            machine.write({'active': False})  # Soft delete
            
            return self._json_response({
                'success': True,
                'message': 'Machine deleted successfully'
            })
        except Exception as e:
            _logger.error(f"Error deleting machine: {e}", exc_info=True)
            return self._json_response({
                'success': False,
                'message': str(e)
            }, status=500)

    # ==================== HELPER METHODS ====================

    def _section_to_dict(self, section):
        """Convert section record to dictionary"""
        return {
            'id': section.id,
            'name': section.name,
            'section_id': section.section_id,
            'location': section.location,
            'created_at': section.created_at.isoformat() if section.created_at else None,
            'updated_at': section.updated_at.isoformat() if section.updated_at else None,
            'machine_count': len(section.machine_ids.filtered(lambda m: m.active)),
        }

    def _machine_to_dict(self, machine):
        """Convert machine record to dictionary"""
        return {
            'id': machine.id,
            'name': machine.name,
            'section_id': machine.section_id.id if machine.section_id else None,
            'section_name': machine.section_id.name if machine.section_id else None,
            'section_location': machine.section_id.location if machine.section_id else None,
            'created_at': machine.created_at.isoformat() if machine.created_at else None,
            'updated_at': machine.updated_at.isoformat() if machine.updated_at else None,
        }

