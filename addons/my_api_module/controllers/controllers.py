# -*- coding: utf-8 -*-
from odoo import http
import json

class MyApiModule(http.Controller):
    @http.route('/my_custom_page', type='http', auth='public', website=True)
    def my_page(self, **kwargs):
        return http.request.render('my_api_module.my_template')
    @http.route('/hellowold', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/my_api_module/my_api_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('my_api_module.listing', {
#             'root': '/my_api_module/my_api_module',
#             'objects': http.request.env['my_api_module.my_api_module'].search([]),
#         })

#     @http.route('/my_api_module/my_api_module/objects/<model("my_api_module.my_api_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('my_api_module.object', {
#             'object': obj
#         })


class StudentApiController(http.Controller):
    
    @http.route('/api/students', auth='public', methods=['GET'], csrf=False)
    def get_students(self, **kwargs):
        students = http.request.env['my_api_module.student'].search([])
        return http.Response(
            json.dumps([{'id': s.id, 'Class': s.Class, 'Name': s.Name} for s in students]),
            content_type='application/json'
        )

    @http.route('/api/students', auth='public', methods=['POST'], csrf=False)
    def create_student(self, **kwargs):
        data = json.loads(http.request.httprequest.data)
        student = http.request.env['my_api_module.student'].create({
            'Class': data.get('Class'),
            'Name': data.get('Name'),
        })
        return http.Response(
            json.dumps({'id': student.id, 'Class': student.Class, 'Name': student.Name}),
            status=201,
            content_type='application/json'
        )

    @http.route('/api/students/<int:student_id>', auth='public', methods=['GET'], csrf=False)
    def get_student(self, student_id, **kwargs):
        try:
            student = http.request.env['my_api_module.student'].browse(student_id)
            if not student.exists():
                return http.Response(
                    json.dumps({'error': 'Student not found'}),
                    status=404,
                    content_type='application/json'
                )
            return http.Response(
                json.dumps({'id': student.id, 'Class': student.Class, 'Name': student.Name}),
                content_type='application/json'
            )
        except Exception as e:
            return http.Response(
                json.dumps({'error': 'Internal Server Error', 'details': str(e)}),
                status=500,
                content_type='application/json'
            )

    @http.route('/api/students/<int:student_id>', auth='public', methods=['PUT'], csrf=False)
    def update_student(self, student_id, **kwargs):
        data = json.loads(http.request.httprequest.data)
        student = http.request.env['my_api_module.student'].browse(student_id)
        if not student.exists():
            return http.Response(status=404)
        student.write({
            'Class': data.get('Class',student.Class),                    
            'Name': data.get('Name', student.Name)
        })
        return http.Response(
            json.dumps({'id': student.id, 'Class': student.Class, 'Name': student.Name}),
            content_type='application/json'
        )

    @http.route('/api/students/<int:student_id>', auth='public', methods=['DELETE'], csrf=False)
    def delete_student(self, student_id, **kwargs):
        student = http.request.env['my_api_module.student'].browse(student_id)
        if not student.exists():
            return http.Response(status=404)
        student.unlink()
        return http.Response(
            json.dumps({'message': 'Student deleted successfully'}),
            status=204,
            content_type='application/json'
        )

        
