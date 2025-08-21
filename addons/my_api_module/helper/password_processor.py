import bcrypt
import logging
_logger = logging.getLogger(__name__)

class PasswordHelper:
    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(
            password = str(password).encode('utf-8'),
            salt = salt
        )
        return hash_password.decode('utf-8')

    # @staticmethod
    # def verify_password(password, hashed_password):
    #     """
    #     Verify password của user với hashed_password
    #     """
    #     try:
    #         password_bytes = password.encode('utf-8')
    #         check = bcrypt.checkpw(
    #             password=password_bytes,
    #             hashed_password=hashed_password
    #         )
    #         return check
    #     except Exception as e:
    #         _logger.error(f"Error verifying password: {e}")
    #         return False
        
    # @staticmethod
    # @staticmethod
    # def is_hashed(password):
    #     """
    #     Kiểm tra password đã được hash chưa
    #     """
    #     if not password:
    #         return False
    #     return password.startswith(('$2$', '$2a$', '$2b$', '$2x$', '$2y$'))