from odoo import models, fields
from enum import Enum 
class StudentAlias2Fields(Enum):
    id = 'id'
    co = 'code'
    fu = 'fullname'
    dob = 'dob'
    sex = 'sex'
    hc = 'homecity'
    addr = 'address'
    hb = 'hobbies'
    hair = 'hair_color'
    em = 'email'
    fb = 'facebook'
    un = 'username'
    pw = 'password'
    de = 'description'
    att = 'attachment'
    att_url = 'attachment_url'

    # cd = 'create_date'
    # wr = 'write_date'
    # cu = 'create_uid'
    # wu = 'write_uid'


class StudentFields2Labels(Enum):
    # id = "ID"
    code = "Mã học sinh"
    fullname = "Tên học sinh"
    dob = "Ngày sinh"
    sex = "Giới tính"
    homecity = "Quê quán"
    address = "Địa chỉ"
    hobbies = "Sở thích"
    hair_color = "Màu tóc"
    email = "Email"
    facebook = "Facebook"
    username = "Tên đăng nhập"
    password = "Mật khẩu"
    description = "Mô tả"
    attachment = "Đường dẫn ảnh"
    attachment_url = "Link ảnh"
    fattachment = "File upload"
    # create_date = 'Ngày tạo'
    # write_date = 'Ngày cập nhật'
    # create_uid = 'Mã Người tạo'
    # write_uid = 'Mã Người cập nhật' 

class Student(models.Model):
    _name = 'my_api_module.student'
    _description = 'Student'
    _rec_name = 'fullname'

    code = fields.Char(string='Student Code',size = 50,  required=True)            
    fullname = fields.Char(string='Full Name',size = 50, required=True)           
    dob = fields.Date(string='Date of Birth', required = True)                          
    sex = fields.Selection([                                            
        ('2', 'Female'),
        ('1', 'Male')
    ], string='Gender', required=True, default='1')  # Mặc định là Nam
    homecity = fields.Char(string='Hometown',size=200)                           # Tỉnh thành
    address = fields.Char(string='Address', size = 200)                             # Địa chỉ chi tiết
    hobbies = fields.Integer(string='Hobbies')                             # Danh sách sở thích (chuỗi 0,1,...)
    hair_color = fields.Char(string='Hair Color', size = 50)                       # Màu tóc
    email = fields.Char(string='Email',size = 200, required = True)                                 # Email liên hệ
    facebook = fields.Char(string='Facebook')                                          # Link Facebook
    username = fields.Char(string='Username',required= True)                           # Tên tài khoản
    password = fields.Char(string='Password', size = 100, required = True)                           # Mật khẩu 
    description = fields.Text(string='Description', size = 200)   
 # Ghi chú
    attachment = fields.Char(string='Attachment')                     # File đính kèm (ảnh/hồ sơ)
    attachment_url = fields.Char(string='Attachment URL')  # URL của file đính kèm
    
    # file_name = fields.Char("Tên file gốc")
    # file_path = fields.Char("Đường dẫn lưu ảnh")
    class_id = fields.Many2one('my_api_module.classes', string='Class')   # Môn học / lớp
   