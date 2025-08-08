import re
from .base_validator import BaseValidator
class StudentValidator(BaseValidator): 
    # @staticmethod
    # def validate_create(data, env):
    #     errors = []
    #     code = data.get('code')
    #     fullname = data.get('fullname')
    #     dob = data.get('dob')
    #     sex = data.get('sex')
    #     email = data.get('email')
    #     username = data.get('username')
    #     password = data.get('password')
    #     facebook = data.get('facebook')

    #     # Kiểm tra bắt buộc
    #     if not code:
    #         errors.append("Mã sinh viên là bắt buộc.")
    #     if not fullname:
    #         errors.append("Họ tên là bắt buộc.")
    #     if not dob:
    #         errors.append("Ngày sinh là bắt buộc.")
    #     if not sex:
    #         errors.append("Giới tính là bắt buộc.")
    #     if not email:
    #         errors.append("Email là bắt buộc.")
    #     if not username:
    #         errors.append("Tên tài khoản là bắt buộc.")
    #     if not password:
    #         errors.append("Mật khẩu là bắt buộc.")

    #     # Kiểm tra độ dài
    #     if code and len(code) > 50:
    #         errors.append("Mã sinh viên tối đa 50 ký tự.")
    #     if fullname and len(fullname) > 100:
    #         errors.append("Họ tên tối đa 100 ký tự.")
    #     if username and len(username) > 50:
    #         errors.append("Tên tài khoản tối đa 50 ký tự.")

    #     # Kiểm tra trùng mã sinh viên
    #     if code and env['my_api_module.student'].search([('code', '=', code)], limit=1):
    #         errors.append("Mã sinh viên đã tồn tại.")
    #     # Kiểm tra trùng username
    #     if username and env['my_api_module.student'].search([('username', '=', username)], limit=1):
    #         errors.append("Tên tài khoản đã tồn tại.")
    #     # Kiểm tra trùng email
    #     if email and env['my_api_module.student'].search([('email', '=', email)], limit=1):
    #         errors.append("Email đã tồn tại.")

    #     regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    #     # Kiểm tra định dạng email đơn giản
    #     if email and not re.fullmatch(regex_email, email):
    #         errors.append("Email không hợp lệ.")

    #     regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
        
    #     if facebook and not re.fullmatch(regex_facebook, facebook):
    #         errors.append("Link Facebook không hợp lệ.")

    #     return errors
    # @staticmethod
    # def validate_update(id, data, env):
    #     errors = []
    #     code = data.get('code')
    #     fullname = data.get('fullname')
    #     dob = data.get('dob')
    #     sex = data.get('sex')
    #     email = data.get('email')
    #     username = data.get('username')
    #     password = data.get('password')
    #     facebook = data.get('facebook')

        
    #     # Kiểm tra độ dài
    #     if code and len(str(code)) > 50:
    #         errors.append("Mã sinh viên tối đa 50 ký tự.")
    #     if fullname and len(fullname) > 100:
    #         errors.append("Họ tên tối đa 100 ký tự.")
    #     if username and len(username) > 50:
    #         errors.append("Tên tài khoản tối đa 50 ký tự.")

    #     # Kiểm tra trùng mã sinh viên
    #     if code and env['my_api_module.student'].search([('code', '=', code),('id', '!=', id)], limit=1):
    #         errors.append("Mã sinh viên đã tồn tại.")
    #     # Kiểm tra trùng username
    #     if username and env['my_api_module.student'].search([('username', '=', username),('id', '!=', id)], limit=1):
    #         errors.append("Tên tài khoản đã tồn tại.")
    #     # Kiểm tra trùng email
    #     if email and env['my_api_module.student'].search([('email', '=', email),('id', '!=', id)], limit=1):
    #         errors.append("Email đã tồn tại.")

    #     regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    #     # Kiểm tra định dạng email 
    #     if email and not re.fullmatch(regex_email, email):
    #         errors.append("Email không hợp lệ.")

    #     regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
    #     #Kiểm tra định dạng facebook
    #     if facebook and not re.fullmatch(regex_facebook, facebook):
    #         errors.append("Link Facebook không hợp lệ.")
    #     # Kiểm tra định dạng ngày sinh
    #     regex_dob = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
    #     if dob and not re.match(regex_dob, dob):
    #         errors.append("Ngày sinh không hợp lệ")
        
    #     return errors
    #     #Kiểm tra định dạng hobbies

    def __init__(self, data = None, model = None):
        super().__init__(data, model)
    
    def constraint_validate(self):
        self.required('code')
        self.required('fullname')
        self.required('dob')
        self.required('sex')
        self.required('email')
        self.required('username')
        self.required('password')
    
    def validate_data(self):
        self.max_length('code', 100)
        self.max_length('fullname', 100)
        self.max_length('username', 100)   
        self.email_check('email')
        self.facebook_check('facebook')
        self.dob_check('dob')
        self.hobbies_check('hobbies')
    
    def validate_create_data(self, data):
        self.data = data
        self.constraint_validate()
        self.validate_data()
        self.unique_value('code', self.model)
        self.unique_value('username', self.model)
        self.unique_value('email', self.model)
        return self.get_errors()
    
    def validate_update_data(self,data, id):
        self.data = data
        self.validate_data()
        self.unique_value('code', self.model, id)
        self.unique_value('username', self.model, id)
        self.unique_value('email', self.model, id)
        return self.get_errors()
        