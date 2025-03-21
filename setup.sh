#!/bin/bash

# 📌 스크립트 실행 중 오류 발생 시 중단
set -e

echo "🚀 Starting Nautilus Setup Script..."

# 📌 NOPASSWD 설정 추가 (가장 먼저 적용)
echo "🚀 Ensuring NOPASSWD is set for current user ($USER)"
NOPASSWD_FILE="/etc/sudoers.d/99-$USER-nopasswd"

if [ ! -f "$NOPASSWD_FILE" ]; then
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee "$NOPASSWD_FILE" > /dev/null
    sudo chmod 0440 "$NOPASSWD_FILE"
    echo "✅ NOPASSWD 설정이 적용되었습니다: $NOPASSWD_FILE"
else
    echo "ℹ️ 이미 NOPASSWD 설정 파일이 존재합니다: $NOPASSWD_FILE"
fi

# 📌 현재 스크립트 위치를 기준으로 경로 설정
TARGET_HOST="localhost"
PASSWARD="keti123"  # sudo 비밀번호 설정
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLAYBOOK_PATH="$SCRIPT_DIR/nautilus/nautilus/workspace/ansible_project/playbook/master_playbook.yaml"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# 📌 Ansible 설치
if ! command -v ansible-playbook &> /dev/null; then
    echo "🚀 Ansible is not installed. Installing Ansible..."
    if [ -f /etc/debian_version ]; then
        sudo apt update
        sudo apt install -y ansible
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y epel-release
        sudo yum install -y ansible
    else
        echo "❌ Unsupported OS. Please install Ansible manually."
        exit 1
    fi
fi

echo "✅ Ansible version:"
ansible --version

# 📌 Python3 / pip3 설치
if ! command -v python3 &> /dev/null; then
    echo "🚀 Installing Python3 and pip3..."
    sudo apt install -y python3 python3-pip
fi

if ! command -v pip3 &> /dev/null; then
    echo "🚀 Installing pip3..."
    sudo apt install -y python3-pip
fi

# 📌 requirements.txt 처리
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "🚀 Installing Python dependencies from requirements.txt..."
    pip3 install --upgrade pip
    pip3 install -r "$REQUIREMENTS_FILE"
    echo "✅ Python dependencies installed successfully!"
else
    echo "⚠️ requirements.txt not found. Skipping Python dependencies installation."
fi

# 📌 sshpass 설치
echo "🚀 Installing sshpass..."
sudo apt-get install -y sshpass

# 📌 Ansible 플레이북 실행
echo "🚀 Running Ansible Playbook: $PLAYBOOK_PATH"
ansible-playbook "$PLAYBOOK_PATH" --extra-vars "target_host=$TARGET_HOST ansible_become_pass=$PASSWARD"
echo "✅ Ansible Playbook execution completed!"

# 📌 Kubernetes 설정
echo "🚀 Setting up Kubernetes kubeconfig for current user..."
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config
echo "✅ KUBECONFIG configured."

# 📌 Docker 재시작 (권한이 적용된 후를 가정)
echo "🚀 Restarting Docker daemon..."
sudo systemctl restart docker
echo "✅ Docker restarted."

echo "🎉 Nautilus setup script completed successfully!"

# 📌 Docker 그룹 적용 안내
echo "ℹ️ Docker group 권한 적용을 위해 터미널을 재시작하거나 로그아웃/로그인 해주세요."
sudo usermod -aG docker $(whoami)

