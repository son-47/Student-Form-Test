import re
import pandas as pd
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
        
    def validate_file_format(self, file):
        """Validate định dạng file"""
        if not file or not hasattr(file, 'filename') or not file.filename:
            self.add_error("File không hợp lệ hoặc không có tên.")
            return False
            
        filename = file.filename.lower()
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            self.add_error("Chỉ hỗ trợ file CSV (.csv) hoặc Excel (.xlsx, .xls).")
            return False
            
        return True
    
    def validate_file_size(self, file, max_size_mb=10):
        """Validate kích thước file"""
        if not file:
            return False
            
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)     # Seek back to start
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if size > max_size_bytes:
            self.add_error(f"File quá lớn. Kích thước tối đa: {max_size_mb}MB.")
            return False
            
        return True
    
    def validate_file_content(self, file):
        """Validate nội dung file và trả về DataFrame"""
        if not self.validate_file_format(file) or not self.validate_file_size(file):
            return None
            
        try:
            filename = file.filename.lower()
            file.seek(0)
            
            if filename.endswith('.csv'):
                content = file.stream.read().decode('utf-8-sig')
                df = pd.read_csv(io.StringIO(content))
            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file.stream)
            else:
                self.add_error("Định dạng file không được hỗ trợ.")
                return None
                
            if df.empty:
                self.add_error("File không chứa dữ liệu.")
                return None
                
            return df
            
        except Exception as e:
            self.add_error(f"Lỗi đọc file: {str(e)}")
            return None
    # def validate_data_rows(self, df, row_validator_func=None):
    #     """Validate từng dòng dữ liệu trong file"""
    #     if df is None:
    #         return []
            
    #     valid_records = []
    #     invalid_rows = []
        
    #     for index, row in df.iterrows():
    #         row_data = row.to_dict()
            
    #         # Loại bỏ NaN values
    #         clean_data = {}
    #         for k, v in row_data.items():
    #             if pd.notna(v) and v is not None:
    #                 clean_data[k] = str(v).strip() if isinstance(v, str) else v
    #             else:
    #                 clean_data[k] = None
            
    #         # Validate từng row nếu có hàm validator
    #         if row_validator_func:
    #             row_errors = row_validator_func(clean_data, index + 2)  # +2 vì header ở row 1
    #             if row_errors:
    #                 invalid_rows.append({
    #                     'row': index + 2,
    #                     'data': clean_data,
    #                     'errors': row_errors
    #                 })
    #                 continue
            
    #         valid_records.append(clean_data)
        
    #     # Báo lỗi nếu có dòng không hợp lệ
    #     if invalid_rows:
    #         error_summary = []
    #         for invalid in invalid_rows[:5]:  # Chỉ hiển thị 5 lỗi đầu
    #             error_summary.append(f"Dòng {invalid['row']}: {'; '.join(invalid['errors'])}")
            
    #         if len(invalid_rows) > 5:
    #             error_summary.append(f"... và {len(invalid_rows) - 5} lỗi khác.")
                
    #         self.add_error(f"File có {len(invalid_rows)} dòng dữ liệu không hợp lệ: " + ' '.join(error_summary))
        
    #     return valid_records
    # def validate_required_columns(self, df, required_columns):
    #     """Validate các cột bắt buộc trong file"""
    #     if df is None:
    #         return False
            
    #     missing_columns = [col for col in required_columns if col not in df.columns]
    #     if missing_columns:
    #         self.add_error(f"File thiếu các cột bắt buộc: {', '.join(missing_columns)}.")
    #         return False
            
    #     return True       