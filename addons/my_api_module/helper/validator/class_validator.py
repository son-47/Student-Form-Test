from .base_validator import BaseValidator
class ClassValidator(BaseValidator):
    # @staticmethod
    # def validate_create(data,model):
    #     errors = []
    #     code = data.get('code')
    #     name = data.get('name')
    #     if not code or not name:
    #         errors.append("Mã lớp và tên lớp là bắt buộc.")

    #     if code and len(code) > 100:
    #         errors.append("Mã lớp tối đa 100 ký tự.")

    #     if name and len(name) > 100:
    #         errors.append("Tên lớp tối đa 100 ký tự.")

    #     # Kiểm tra trùng mã lớp
    #     if code and model['my_api_module.classes'].search([('code', '=', code)], limit=1):
    #         errors.append("Mã lớp đã tồn tại.")

    #     return errors
    
    # @staticmethod
    # def validate_update(id, data, model):
    #     errors = []
    #     code = data.get('code')
    #     name = data.get('name')
    #     # class_id = data.get('id')

    #     # if not class_id:
    #     #     errors.append("Thiếu ID lớp cần cập nhật.")

    #     if code and len(code) > 100:
    #         errors.append("Mã lớp tối đa 100 ký tự.")

    #     if name and len(name) > 100:
    #         errors.append("Tên lớp tối đa 100 ký tự.")

    #     # Kiểm tra trùng mã lớp (không tính chính bản ghi đang sửa)
    #     if code:
    #         domain = [('code', '=', code), ('id', '!=', id)]
    #         if model['my_api_module.classes'].search(domain, limit=1):
    #             errors.append("Mã lớp đã tồn tại.")

    #     return errors

    def __init__(self, data=None, model = None):
        super().__init__(data, model)

    def constraint_validate(self):
        self.required('code')
        self.required('name')

    def validate_data(self):
        self.max_length('code', 100)
        self.max_length('name', 100)

    def validate_create_data(self, data):
        self.data = data
        self.unique_value('code', self.model)
        self.constraint_validate()
        self.validate_data()
        return self.get_errors()

    def validate_update_data(self, data, id):
        self.data = data
        self.validate_data()
        self.unique_value('code', self.model, id)
        return self.get_errors()


