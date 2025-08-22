import jwt
import datetime
import json
from odoo.http import request

from ..helper.response_format import responseFormat

class AuthController:
    def __init__(self, model_name):
        self.model_name = model_name

    def register(self):
        data = json.loads(request.httprequest.data)
        print(data)
        user_name = data['username']
        password = data['password']
        if not user_name or not password:
            return responseFormat("Error", "Khong nhan duoc thong tin dang nhap")
        try:
            user = request.env[self.model_name].sudo().create({
                'user_name': user_name,
                'password': password,
                'role': 'user',
            })
            jwt_payload = {
                'user_id': user.id,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            token = jwt.encode(jwt_payload, 'your_secret_key', algorithm='HS256')
            return responseFormat(200, "Dang ky thanh cong", data={
                'user_id': user.id,
                'role': user.role,
                'token': token,
            })
        except Exception as e:
            return responseFormat("Error", f"Dang ky khong thanh cong: {str(e)}")
        

    def login(self):
        data = json.loads(request.httprequest.data)
        user_name = data.get('username', None)
        password = data.get('password', None)
        if not user_name or not password:
            return responseFormat("Error", "Khong nhan duoc thong tin dang nhap", oldData={
                'username': user_name,
                'password': password
            })
        try:
            user = request.env[self.model_name].sudo().search([
                ('user_name', '=', user_name)
            ], limit=1)
            if not user:
                return responseFormat("Error", "Tai khoan khong ton tai", oldData={
                    'username': user_name,
                    'password': password
                })
            if user.password != password:
                return responseFormat("Error", "Mat khau khong dung", oldData={
                    'username': user_name,
                    'password': password
                })
            jwt_payload = {
                'user_id': user.id,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            token = jwt.encode(jwt_payload, 'your_secret_key', algorithm='HS256')
            return responseFormat(200, "Dang nhap thanh cong", data={
                'user_id': user.id,
                'role': user.role,
                'token': token,
            })
        except Exception as e:
            return responseFormat("Error", f"Dang nhap khong thanh cong: {str(e)}")