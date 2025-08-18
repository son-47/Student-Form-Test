import json,os
from odoo import http
from odoo.http import request
from ..helper.upload_config import get_upload_config
import logging
_logger = logging.getLogger(__name__)
from ..controllers.Student_controller_test import StudentController
import mimetypes

class StudentRoute(http.Controller):
    @http.route('/images/<filename>', type='http', auth='public',methods=['GET'])
    def serve_image(self, filename):
        """Serve uploaded images"""
        try:
            upload_type, config = get_upload_config()
            if upload_type == "local":
                filepath = os.path.join(config['base_dir'],'images', filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        mime_type, _ = mimetypes.guess_type(filename)
                        if not mime_type:
                            mime_type = 'application/octet-stream'
                        return request.make_response(
                            f.read(),
                            headers=[
                                ('Content-Type', mime_type),
                                ('Content-Disposition', f'inline; filename="{filename}"')
                            ]
                        )
            _logger.warning(f"[DEBUG] File requested: {filename}, Path checked: {filepath}")
            return request.not_found()
        except Exception as e:
            _logger.error(f"Error serving image: {e}")
            return request.not_found()
        
    @http.route('/tra_student', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all(self, **kw):
        return StudentController().get_all(kw)

    @http.route('/tra_student/page/<int:page>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_by_page(self, page, **kw):
        return StudentController().get_by_page(page, kw)

    @http.route('/tra_student', type='http', auth='public', methods=['POST'], csrf=False)
    def store(self, **kw):
        return StudentController().store(kw)

    @http.route('/tra_student/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_by_id(self, id, **kw):
        return StudentController().get_by_id( id, kw)

    @http.route('/tra_student/<int:id>', type='http', auth='public', methods=['PUT','POST'], csrf=False)
    def update(self, id, **kw):
        return StudentController().update(id, kw)

    @http.route('/tra_student/<int:id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def destroy(self, id):
        return StudentController().destroy(id)

    @http.route('/tra_student/copy/<int:id>', type='http', auth='public', methods=['POST'], csrf=False)
    def copy(self, id):
        return StudentController().copy(id)

    @http.route('/tra_student/delete', type='http', auth='public', methods=['DELETE'], csrf=False)
    def mass_delete(self, **kw):
        return StudentController().mass_delete(kw)

    @http.route('/tra_student/copy', type='http', auth='public', methods=['POST'], csrf=False)
    def mass_copy(self, **kw):
        return StudentController().mass_copy(kw)

    @http.route('/tra_student/import', type='http', auth='public', methods=['POST'], csrf=False)
    def import_data(self, **kw):
        return StudentController().import_data(kw)

    @http.route('/tra_student/export/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def export_by_id(self, id, **kw):
        return StudentController().export_by_id(id, kw)

    @http.route('/tra_student/export', type='http', auth='public', methods=['POST'], csrf=False)
    def mass_export(self, **kw):
        return StudentController().mass_export(kw)