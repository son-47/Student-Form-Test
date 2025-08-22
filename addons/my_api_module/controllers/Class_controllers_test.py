from .base_controller import BaseController
from odoo.http import request
from ..helper.validator.class_validator import ClassValidator
from ..models.classes import ClassAlias2Fields, ClassFields2Labels

class ClassController(BaseController):
    def __init__(self):
        validator = ClassValidator(model = request.env['my_api_module.classes'], modelFields2Labels = ClassFields2Labels)
        super().__init__('my_api_module.classes', validator)
        self.modelAlias2Fields = ClassAlias2Fields
        self.modelFields2Labels = ClassFields2Labels
        self.fieldList = [field.name for field in self.modelFields2Labels]
        self.labelList = [field.value for field in self.modelFields2Labels]
        