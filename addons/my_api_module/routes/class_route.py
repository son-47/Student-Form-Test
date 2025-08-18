# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request

# local package
from ..controllers.Class_controllers_test import ClassController


class ClassRoute(http.Controller):

    @http.route('/tra_class', type='http', auth='public', methods=['GET'], csrf=False)
    def get_all(self, **kw):
        return ClassController().get_all(kw)

    @http.route('/tra_class/page/<int:init>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_by_page(self, init, **kw):
        return ClassController().get_by_page(init, kw)
    
    @http.route('/tra_class',type ='http', auth ='public', methods =['POST'], csrf=False)
    def store(self, **kw):
        return ClassController().store(kw)
    
    @http.route('/tra_class/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_by_id(self, id, **kw):
        return ClassController().get_by_id(id, kw)

    @http.route('/tra_class/<int:id>', type='http', auth='public', methods=['PUT','POST'], csrf=False)
    def update(self, id, **kw):
        return ClassController().update( id, kw)

    @http.route('/tra_class/<int:id>', type='http', auth='public', methods=['DELETE'], csrf=False)
    def destroy(self, id):
        return ClassController().destroy(id)

    @http.route('/tra_class/copy/<int:id>', type='http', auth='public', methods=['POST'], csrf=False)
    def copy(self, id):
        return ClassController().copy(id)

    @http.route('/tra_class/delete', type='http', auth='public', methods=['DELETE'], csrf=False)
    def mass_delete(self, **kw):
        return ClassController().mass_delete(kw)

    @http.route('/tra_class/copy', type='http', auth='public', methods=['POST'], csrf=False)
    def mass_copy(self, **kw):
        return ClassController().mass_copy(kw)

    @http.route('/tra_class/import', type='http', auth='public', methods=['POST'], csrf=False)
    def import_data(self, **kw):
        return ClassController().import_data(kw)

    @http.route('/tra_class/export/<int:id>', type='http', auth='public', methods=['GET'], csrf=False)
    def export_by_id(self, id, **kw):
        return ClassController().export_by_id(id, kw)

    @http.route('/tra_class/export', type='http', auth='public', methods=['POST'], csrf=False)
    def mass_export(self, **kw):
        return ClassController().mass_export(kw)