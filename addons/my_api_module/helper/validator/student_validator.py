from .base_validator import BaseValidator

class StudentValidator(BaseValidator): 
    def __init__(self, data=None, model=None):
        super().__init__(data, model)
    
    def _define_rules(self):
        """Định nghĩa rules khác nhau cho CREATE và UPDATE"""
        
        # CREATE RULES 
        self.define_create_rules({
            "code": ["required", "unique_value", "range_length:3,50"],
            "fullname": ["required", "range_length:3,50"],
            "email": ["required", "unique_value", "email", "max_length:200"],
            "username": ["required", "unique_value", "range_length:4,50"],
            "password": ["required", "range_length:8,50"],
            "dob": ["required", "dob"],
            "sex": ["required"],
            "facebook": ["facebook"],
            "hobbies": ["hobbies"],
            "description": ["max_length:200"],
            "hair_color": ["max_length:50"],
            "address": ["max_length:200"],
            "fattachment":["image", "max_size:"]
        })
        
        # UPDATE RULES 
        self.define_update_rules({
            "code": ["unique_value", "range_length:3,50"],  
            "fullname": ["range_length:3,50"],          
            "email": ["email"],        
            "username": ["range_length:4,50"], 
            "password": ["range_length:8,50"],            
            "dob": ["dob"],                                                              
            "facebook": ["facebook"],
            "hobbies": ["hobbies"],
            "description": ["max_length:200"],
            "hair_color": ["max_length:50"],
            "address": ["max_length:200"]
        })
      
    # def constraint_validate(self):
    #     self.required('code')
    #     self.required('fullname')
    #     self.required('dob')
    #     self.required('sex')
    #     self.required('email')
    #     self.required('username')
    #     self.required('password')
    
    # def validate_data(self):
    #     self.max_length('code', 100)
    #     self.max_length('fullname', 100)
    #     self.max_length('username', 100)   
    #     self.email_check('email')
    #     self.facebook_check('facebook')
    #     self.dob_check('dob')
    #     self.hobbies_check('hobbies')
    
    # def validate_create_data(self, data):
    #     self.data = data
    #     self.constraint_validate()
    #     self.validate_data()
    #     self.unique_value('code', self.model)
    #     self.unique_value('username', self.model)
    #     self.unique_value('email', self.model)
    #     return self.get_errors()
    
    # def validate_update_data(self,data, id):
    #     self.data = data
    #     self.validate_data()
    #     self.unique_value('code', self.model, id)
    #     # self.unique_value('username', self.model, id)
    #     # self.unique_value('email', self.model, id)
    #     return self.get_errors()
        
    # def validate_import_file(self, file):
    #     """Validate file import sinh viên - TẬN DỤNG CÁC HÀM CÓ SẴN"""
    #     self.errors = []  # Reset errors
        
    #     # 1. Validate định dạng và nội dung file 
    #     df = self.validate_file_content(file)
    #     if df is None:
    #         return None, []
        
    #     # 2. Validate các cột bắt buộc 
    #     required_columns = ['code', 'fullname', 'email', 'username', 'password','dob', 'sex', 'hobbies']
    #     if not self.validate_required_columns(df, required_columns):
    #         return None, []
        
    #     # 3. Validate từng dòng dữ liệu 
    #     # valid_records = self.validate_data_rows(df, self._validate_student_row)
        
    #     return df
    
    # def validate_update_file(self, file):
    #     """Validate file update thông tin sinh viên"""
    #     self.errors = []
        
    #     # Validate định dạng và nội dung (SỬ DỤNG HÀM CÓ SẴN)
    #     df = self.validate_file_content(file)
    #     if df is None:
    #         return None
        
    #     if len(df) != 1:
    #         self.add_error("File cập nhật chỉ được chứa đúng 1 dòng dữ liệu.")
    #         return None
        
    #     # Validate dòng đầu tiên (SỬ DỤNG HÀM CÓ SẴN)
    #     row_data = df.iloc[0].to_dict()
    #     clean_data = {}
    #     for k, v in row_data.items():
    #         if pd.notna(v) and v is not None:
    #             clean_data[k] = str(v).strip() if isinstance(v, str) else v
        
    #     # SỬ DỤNG TRỰC TIẾP CÁC HÀM VALIDATE CÓ SẴN
    #     temp_data = self.data  # Backup data hiện tại
    #     self.data = clean_data  # Set data mới để validate
        
    #     # Validate từng field bằng các hàm có sẵn
    #     self._validate_student_fields_update()
        
    #     self.data = temp_data  # Restore data cũ
        
    #     return clean_data if not self.errors else None
    
    # def _validate_student_row(self, row_data, row_number):
    #     """Validate một dòng dữ liệu sinh viên - TẬN DỤNG CÁC HÀM CÓ SẴN"""
    #     # Backup data hiện tại
    #     temp_data = self.data
    #     temp_errors = self.errors
        
    #     # Set data mới để validate
    #     self.data = row_data
    #     self.errors = []
        
  
    #     self.constraint_validate()  
    #     self.validate_data()       
        
    #     # Lấy errors của dòng này
    #     row_errors = self.errors.copy()
        
    #     # Restore data và errors ban đầu  
    #     self.data = temp_data
    #     self.errors = temp_errors
        
    #     return row_errors
    
    # def _validate_student_fields_update(self):
    #     """Validate các field cho update"""
    #     # Không check required cho update, chỉ check format và unique
        
       
    #     if self.data.get('email'):
    #         self.email_check('email')
        
         
    #     if self.data.get('dob'):
    #         self.dob_check('dob')
        
        
    #     if self.data.get('facebook'):
    #         self.facebook_check('facebook')
        
       
    #     if self.data.get('hobbies'):
    #         self.hobbies_check('hobbies')
        
        
    #     if self.data.get('code'):
    #         self.max_length('code', 100)
    #     if self.data.get('fullname'):
    #         self.max_length('fullname', 100)
    #     if self.data.get('username'):
    #         self.max_length('username', 100)
    #     if self.data.get('description'):
    #         self.max_length('description', 100)
        
       
    #     if self.data.get('code'):
    #         self.unique_value('code', self.model)
    #     if self.data.get('username'):
    #         self.unique_value('username', self.model)
    #     if self.data.get('email'):
    #         self.unique_value('email', self.model)