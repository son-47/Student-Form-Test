from .base_controller import BaseController
from odoo.http import request
# from ..helper.validator.class_validator import ClassValidator
from ..models.classes import ClassAlias2Fields, ClassFields2Labels
from ..helper.validator.base_validator import BaseValidator

class ClassController(BaseController):
    def __init__(self):
        validator = self._create_validator()
        super().__init__('my_api_module.classes', validator)
        self.modelAlias2Fields = ClassAlias2Fields
        self.modelFields2Labels = ClassFields2Labels
        self.fieldList = [field.name for field in self.modelFields2Labels]
        self.labelList = [field.value for field in self.modelFields2Labels]

    def _create_validator(self):
        """Tạo validator với rules riêng cho Class"""
        validator = BaseValidator(model=request.env['my_api_module.classes'].sudo(), 
                                modelFields2Labels=ClassFields2Labels)

        validator.define_field_rules({
            "code": {"required": True, "unique": True, "min_length": 3, "max_length": 50},
            "name": {"required": True, "min_length": 2, "max_length": 100},
            "description": {"max_length": 500},
            "attachment": {"file_name": True}
        })

        return validator

    # def has_image_support(self):
    #     return True

    # def get_image_field_name(self):
    #     return 'fattachment'
    def get_search_domain(self, search_term):
        """Search domain cho Class"""
        if not search_term:
            return []
        
        return [
            '|', ('name', 'ilike', search_term),
            '|', ('description', 'ilike', search_term),
            ('code', 'ilike', search_term)
        ]