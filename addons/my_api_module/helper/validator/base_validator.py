import re
class BaseValidator:
    """
    regex: [] 1 ký tự duy nhất
    Khởi tạo bộ Validator tổng quát
    - Danh sách các thuộc tính:
        +data: dictionary chứa dữ liệu cần kiểm tra
    - Các quy tắc kiểm tra:
        - required: Kiểm tra trường bắt buộc
        - max_length: Kiểm tra độ dài tối đa của trường
        -unique_value: Kiểm tra trường bắt buộc
        - email_check: Kiểm tra định dạng email
        - facebook_check: Kiểm tra định dạng facebook
        - dob_check: Kiểm tra định dạng ngày sinh
        - hobbies_check: Kiểm tra dữ liệu hobbies
        - add_error: Thêm lỗi vào danh sách lỗi
        - errors: Lưu trữ các lỗi đã xảy ra trong quá trình kiểm tra
    """
    def __init__(self, data=None, model = None):
        self.data = data or {}  
        self.errors = []
        self.model = model

    def get_errors(self):
        return self.errors
    
    def add_error(self, message):
        if message:
            self.errors.append(message)

    def required(self, field):
        value = self.data.get(field)
        if value is None or str(value).strip() == "":
            self.add_error(f"{field} là bắt buộc.")

    def max_length(self, field, max_length):
        value = self.data.get(field)
        if isinstance(value, str):
            value = value.strip()
        elif value is not None:
            value = str(value).strip()
        else:
            value = ""

        if len(value) > max_length:
            self.add_error(f"{field} tối đa {max_length} ký tự.")


    def unique_value(self, field, model, except_id = None):
        value = self.data.get(field)
        if value is None:
            return 
        value = str(value).strip()
        domain = [(field, '=', value)]
        if except_id:
            domain.append(('id', '!=', except_id))
        if model.search(domain, limit = 1):
            self.add_error(f" {field} đã tồn tại.")
            
    def email_check(self, field):
        value = self.data.get(field, '')
        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}\b'
        if value and not re.match(regex_email, value):
            self.add_error("Email không đúng định dạng.")
    
    def facebook_check(self, field):
        value = self.data.get(field, '')
        regex_facebook = r'^(https?:\/\/)?(www\.)?facebook\.com\/[A-Za-z0-9\.]+\/?$'
        if value and not re.match(regex_facebook, value):
            self.add_error("Facebook không đúng định dạng.")
        
    def dob_check(self, field):
        value = self.data.get(field, '')
        regex_dob = r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
        if value  and not re.match(regex_dob, value):
            self.add_error("Ngày sinh không đúng định dạng.")
            
    def hobbies_check(self, field):
        value = self.data.get(field)
        if not isinstance(value, str) or len(value) != 57:
            self.add_error("Hobbies phải là ký tự có độ dài 57.")
        else :
            regex_hobbies =  r'^(0|1)(,(0|1)){28}$'
            if value and not re.match(regex_hobbies, value):
                self.add_error("Hobbies không đúng định dạng.")
        
            