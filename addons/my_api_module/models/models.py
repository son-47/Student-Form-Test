

field_alias = {'co': 'code', 'na': 'name', 'de': 'description', 'wr': 'write_date'}
columnlist = "co , na,  de"
# columns = []
# for alias in columnlist.split(','):
#     field = field_alias.get(alias.strip())
#     columns.append(field)
# print(columns)
# try:
#     try:
#         x = int(input("Enter a number: "))
#         print("You entered:", x)
#     except Exception :
#         raise ValueError("lỗi không phải int")
# except ValueError as ve:
#     print(ve)
# except Exception as e:
#     print(e)
        

# try:
#     x = int(input("Enter a number: "))
#     print("You entered:", x)
# except Exception as e:
#     raise TypeError("lỗi không phải int")
#     print(e)
from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "test"
MINIO_SECURE = False  # True nếu dùng https

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def upload_file_to_minio(file_path, filename=None, content_type="image/jpeg"):
    """
    Upload file từ đường dẫn file_path lên MinIO bucket 'test'
    """
    if not filename:
        import os
        filename = os.path.basename(file_path)
    # Tạo bucket nếu chưa có
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
    # Upload file
    with open(file_path, "rb") as file_data:
        file_stat = file_data.seek(0, 2)
        file_data.seek(0)
        client.put_object(
            MINIO_BUCKET,
            filename,
            file_data,
            length=file_stat,
            content_type=content_type
        )
    url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{filename}"
    return url

if __name__ == "__main__":
    # Thay đường dẫn file test bên dưới bằng file ảnh thực tế trên máy bạn
    file_path = "C:/Users/PC/Downloads/b7ccc8c3-3cb1-47a9-9292-7846de773239.jpg"
    try:
        url = upload_file_to_minio(file_path)
        print(f"Upload thành công! Ảnh truy cập tại: {url}")
    except S3Error as err:
        print(f"Lỗi MinIO: {err}")
    except Exception as e:
        print(f"Lỗi khác: {e}")