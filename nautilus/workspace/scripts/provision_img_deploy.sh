#!/bin/bash

# 설정
MINIO_ALIAS="myminio"
MINIO_BUCKET="images"
IMAGE_NAME="nautilus-dev-img.tar"
LOCAL_WORKSPACE="$(dirname "$(realpath "$0")")/.."  # 상대 경로 설정
CONTAINER_NAME="nautilus-container"
NEW_IMAGE_NAME="nautilus-dev-updated"
NEW_IMAGE_TAR="nautilus-dev-updated.tar"
MINIO_UPLOAD_PATH="$MINIO_ALIAS/$MINIO_BUCKET/$NEW_IMAGE_TAR"

# MinIO 연결 설정
mc alias set $MINIO_ALIAS http://localhost:9000 minioadmin minioadmin

# MinIO에서 이미지 다운로드
mc cp $MINIO_ALIAS/$MINIO_BUCKET/$IMAGE_NAME $LOCAL_WORKSPACE/

# Docker 이미지 로드
docker load -i $LOCAL_WORKSPACE/$IMAGE_NAME

# 이미지 ID 확인 및 컨테이너 실행
IMAGE_ID=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep "nautilus")
docker run -dit --name $CONTAINER_NAME $IMAGE_ID /bin/bash

# 프로젝트 YAML 파일 컨테이너로 복사
docker cp $LOCAL_WORKSPACE/provisioning/project.yml $CONTAINER_NAME:/workspace/nautilus/workspace/provisioning/

# 컨테이너 내에서 스크립트 실행
docker exec -it $CONTAINER_NAME python /workspace/nautilus/nautilus/api/etc/provision.py

# 변경된 컨테이너를 새로운 이미지로 커밋
docker commit $CONTAINER_NAME $NEW_IMAGE_NAME

# # 새로운 이미지를 tar 파일로 저장
# docker save -o $LOCAL_WORKSPACE/$NEW_IMAGE_TAR $NEW_IMAGE_NAME
# # MinIO에 tar 파일 업로드
# mc cp $LOCAL_WORKSPACE/$NEW_IMAGE_TAR $MINIO_UPLOAD_PATH

# docker save 결과를 바로 MinIO로 업로드 (중간에 로컬 .tar 파일을 만들지 않고 바로 MinIO에 저장)
docker save $NEW_IMAGE_NAME | mc pipe $MINIO_UPLOAD_PATH

echo "Deployment completed successfully. New image stored in MinIO: $MINIO_UPLOAD_PATH"
