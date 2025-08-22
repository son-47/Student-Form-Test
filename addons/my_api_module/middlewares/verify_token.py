import jwt
from functools import wraps
from odoo.http import request, Response

JWT_SECRET = 'your_secret_key'
JWT_ALGORITHM = 'HS256'

def verify_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response("Khong nhan duoc token", status=401)

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.user_id = decoded.get('user_id')
            print("User ID:", request.user_id)
            request.user_role = decoded.get('role')
            print("User Role:", request.user_role)
        except jwt.ExpiredSignatureError:
            return Response("Token da het han", status=401)
        except jwt.InvalidTokenError:
            return Response("Token khong hop le", status=401)

        return func(*args, **kwargs)
    return wrapper