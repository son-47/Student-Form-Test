# /mnt/extra-addons/my_api_module/controllers/Student_controller_test.py
from odoo.http import request
from .base_controller import BaseController  # Nhập BaseController từ base_controller.py
from ..models.student import StudentAlias2Fields,StudentFields2Labels
from..helper.validator.base_validator import BaseValidator
# from ..helper.validator.student_validator import StudentValidator

class StudentController(BaseController):  # Kế thừa từ BaseController, không phải ClassController
    def __init__(self):
        validator = self._create_validator()
        super().__init__('my_api_module.student', validator)
        self.modelAlias2Fields = StudentAlias2Fields
        self.modelFields2Labels = StudentFields2Labels
        self.fieldList = [field.name for field in self.modelFields2Labels]
        self.labelList = [field.value for field in self.modelFields2Labels]
        
        self.file_list = [("attachment", "enbadsfsdfs")]
        
    def _create_validator(self):
        """Tạo validator với rules riêng cho Student"""
        validator = BaseValidator(model=request.env['my_api_module.student'].sudo(), 
                                modelFields2Labels=StudentFields2Labels)
        
        validator.define_field_rules({
            "code": {"required": True, "unique": True, "min_length": 3, "max_length": 50},
            "fullname": {"required": True, "min_length": 2, "max_length": 50},
            "email": {"required": True, "unique": True, "url": True, "max_length": 200},
            "username": {"required": True, "unique": True, "min_length": 4, "max_length": 50},
            "password": {"required": True, "min_length": 8, "max_length": 100},
            "dob": {"required": True, "date": True},
            "sex": {"required": True},
            "facebook": {"url": True},
            "hobbies": {"list": True},
            "description": {"max_length": 200},
            "hair_color": {"max_length": 50},
            "address": {"max_length": 200},
            "homecity": {"max_length": 200},
            "fattachment": {"file_size": 5, "file_name": True},
            "attachment": {"file_name": True}
        })
        
        return validator
    
    def has_image_support(self):
        return True
    
    def get_image_field_name(self):
        return 'fattachment'
    
    def get_search_domain(self, search_term):
        """Search domain cho Student"""
        if not search_term:
            return []
        
        return [
            '|', ('fullname', 'ilike', search_term),
            '|', ('code', 'ilike', search_term),
            '|', ('email', 'ilike', search_term),
            ('username', 'ilike', search_term)
        ]