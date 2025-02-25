#!/bin/bash

echo "test completed successfully."
#!/bin/bash

# 설정
MINIO_ALIAS="myminio"
MINIO_BUCKET="images"
IMAGE_NAME="nautilus-dev-img.tar"
LOCAL_WORKSPACE="$(dirname "$(realpath "$0")")/.."  # 상대 경로 설정
CONTAINER_NAME="nautilus-container"
NEW_IMAGE_NAME="nautilus-dev-updated"
NEW_IMAGE_TAR="nautilus-dev-updated.tar"

echo "Deployment $LOCAL_WORKSPACE"

