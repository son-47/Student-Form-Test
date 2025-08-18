UPLOAD_CONFIG = {
    "type": "minio",  # "local" hoặc "minio"
    
    "local": {
        "base_dir": "/mnt/odoo_project/addons/my_api_module/static/uploads",
        "base_url": "http://172.27.100.251:8069"
    },
    
    "minio": {
        "endpoint": "10.0.0.10:9000",
        "access_key": "deftDe1qhfYjxAdC", 
        "secret_key": "ozxaOSclRvu4wFXD6LxU6Nc61WrTKMb4",
        "bucket": "test",
        "secure": False
    }
}

def get_upload_config():
    """Lấy cấu hình upload hiện tại"""
    upload_type = UPLOAD_CONFIG["type"]
    return upload_type, UPLOAD_CONFIG[upload_type]