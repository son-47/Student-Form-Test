import jwt
import datetime
import json
import logging
from odoo.http import request

from ..helper.response_format import responseFormat
from ..helper.password_processor import PasswordHelper

_logger = logging.getLogger(__name__)
class AuthController:
    def __init__(self, model_name):
        self.model_name = model_name
    
    def register(self):
        try:
            if hasattr(request, 'httprequest') and request.httprequest.data:
                data = json.loads(request.httprequest.data)
            else:
                return responseFormat("Error", "Không nhận được thông tin đăng ký")
            user_name = data.get('username')
            password = data.get('password')
            if not user_name or not password:
                return responseFormat("Error", "Username và password không được bỏ trống")
            exit_user = request.env[self.model_name].sudo().search([('user_name', '=', user_name)], limit = 1)
            if exit_user:
                return responseFormat("Error", "Username đã tồn tại")
            #Hash password trước khi lưu
            hashed_password = PasswordHelper.hash_password(password)
            #Tạo user mới
            user = request.env[self.model_name].create({
                'user_name': user_name,
                'password': hashed_password,
                'role': 'user'
            })
            jwt_payload = {
                'user_id': user.id,
                'username': user.user_name,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            token = jwt.encode(jwt_payload, 'your_secret_key', algorithm='HS256')
            return responseFormat(200, "Đăng ký thành công", data ={
                'user_id':user.id,
                'username': user.user_name,
                'role': user.role,
                'token': token 
            })
        except Exception as e:
            return responseFormat("Error", f"Đăng ký không thành công : {str(e)}")
    
    def login(self):
        try:
            if hasattr(request, 'httprequest') and request.httprequest.data:
                data = json.loads(request.httprequest.data)
            else:
                return responseFormat("Error", "Không nhận được thông tin đăng nhập")
            user_name = data.get('username')
            password = data.get('password')
            
            if not user_name or not password:
                return responseFormat("Error", "Username và password không được bỏ trống", oldData={
                    'username': user_name
                    # 'password': password
                })
            #Tìm user theo username
            user = request.env[self.model_name].sudo().search([('user_name', '=', user_name)], limit=1)
            if not user:
                return responseFormat("Error", "Tài khoản không tồn tại", oldData = {
                    'username': user_name
                })
            
            check_pass = PasswordHelper.verify_password(password, user.password)
            if not check_pass:
                return responseFormat("Error", "Mật khẩu không đúng", oldData = {
                    'username': user_name
                })
            jwt_payload = {
                'user_id': user.id,
                'username': user.user_name,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            token = jwt.encode(jwt_payload, 'your_secret_key', algorithm='HS256')
            
            return responseFormat(200, "Đăng nhập thành công", data ={
                'user_id': user.id,
                'username': user.user_name,
                'role': user.role,
                'token':token
            })
        except Exception as e:
            return responseFormat("Error", f"Đăng nhập không thành công : {str(e)}")