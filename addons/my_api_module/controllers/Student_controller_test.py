# /mnt/extra-addons/my_api_module/controllers/Student_controller_test.py
from odoo.http import request
from .base_controller import BaseController  # Nhập BaseController từ base_controller.py
from ..models.student import StudentAlias2Fields,StudentFields2Labels
from ..helper.validator.student_validator import StudentValidator

class StudentController(BaseController):  # Kế thừa từ BaseController, không phải ClassController
    def __init__(self):
        validator = StudentValidator(model = request.env['my_api_module.student'])
        super().__init__('my_api_module.student', validator)
        self.modelAlias2Fields = StudentAlias2Fields
        self.modelFields2Labels = StudentFields2Labels
        self.fieldList = [field.name for field in self.modelFields2Labels]
        self.labelList = [field.value for field in self.modelFields2Labels]
        
