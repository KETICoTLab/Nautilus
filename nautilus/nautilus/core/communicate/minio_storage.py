# communicate minio
from minio import Minio
import tempfile
import os

# MinIO 클라이언트 생성
### 나중에 Config에 저장해놓고 불러와야 됨
client = Minio(
  "10.252.73.35:9000",  # MinIO 서버 주소 (예: 'localhost:9000')
  access_key="minio",
  secret_key="minio123",
  secure=False  # HTTPS를 사용할 경우 True로 설정
)

bucket_name = "images"
default_tar_name = "nautilus-default-img.tar"
local_file_path = os.path.join(tempfile.gettempdir(), default_tar_name)
pv_tar_name = "nautilus-pv-updated.tar"
pv_file_path = os.path.join(tempfile.gettempdir(), pv_tar_name)


def pull_default_image_tar_from_minio(minio_client=client, bucket_name=bucket_name, tar_file_name=default_tar_name, local_file_path=local_file_path):
  """
  Minio에서 .tar 파일을 로컬로 다운로드.
  """
  try:
    minio_client.fget_object(bucket_name, tar_file_name, local_file_path)
    print(f"Downloaded {tar_file_name} from Minio to {local_file_path}")
    return local_file_path
  except Exception as e:
    print(f"Failed to download {tar_file_name} from Minio: {e}")
    raise

def pull_pv_image_tar_from_minio(minio_client=client, bucket_name=bucket_name, tar_file_name=pv_tar_name, local_file_path=pv_file_path):
  """
  Minio에서 .tar 파일을 로컬로 다운로드.
  """
  try:
    minio_client.fget_object(bucket_name, tar_file_name, local_file_path)
    print(f"Downloaded {tar_file_name} from Minio to {local_file_path}")
    return local_file_path
  except Exception as e:
    print(f"Failed to download {tar_file_name} from Minio: {e}")
    raise

def push_image_tar_from_minio(minio_client=client, bucket_name=bucket_name, tar_file_name=pv_tar_name, local_file_path=pv_file_path) :
  """
  Minio에서 .tar 파일을 로컬로 업로드.
  """
  # 버킷 존재 확인 & 없으면 생성
  if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)
  try:
    minio_client.fput_object(bucket_name, tar_file_name, local_file_path)
    print(f"Uploaded {tar_file_name} to Minio from {local_file_path}")
  except Exception as e:
    print(f"Failed to upload {tar_file_name} to Minio: {e}")
    raise
