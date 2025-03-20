#!/bin/bash

# 📌 스크립트 실행 중 오류 발생 시 중단
set -e

# 📌 현재 스크립트 위치를 기준으로 경로 설정
TARGET_HOST="localhost"
PASSWARD="keti123"  # sudo 비밀번호 설정
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLAYBOOK_PATH="$SCRIPT_DIR/nautilus/nautilus/workspace/ansible_project/playbook/master_playbook.yaml"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

# 📌 Ansible이 설치되어 있는지 확인
if ! command -v ansible-playbook &> /dev/null; then
    echo "🚀 Ansible is not installed. Installing Ansible..."
    
    # ✅ Ubuntu / Debian 기반 시스템
    if [ -f /etc/debian_version ]; then
        sudo apt update
        sudo apt install -y ansible

    # ✅ CentOS / RHEL 기반 시스템
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y epel-release
        sudo yum install -y ansible

    else
        echo "❌ Unsupported OS. Please install Ansible manually."
        exit 1
    fi
fi

# 📌 Ansible 버전 확인
echo "✅ Ansible version:"
ansible --version

# 📌 Python 및 pip 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "🚀 Python3 is not installed. Installing Python3..."
    sudo apt install -y python3 python3-pip
fi

if ! command -v pip3 &> /dev/null; then
    echo "🚀 pip3 is not installed. Installing pip3..."
    sudo apt install -y python3-pip
fi

# 📌 Python 패키지 설치 (`requirements.txt`가 존재하는 경우)
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "🚀 Installing Python dependencies from requirements.txt..."
    pip3 install --upgrade pip  # 최신 버전으로 업데이트
    pip3 install -r "$REQUIREMENTS_FILE"
    echo "✅ Python dependencies installed successfully!"
else
    echo "⚠️ requirements.txt not found. Skipping Python dependencies installation."
fi

# 📌 sshpass Install
echo "🚀 Installing sshpass"
sudo apt-get install sshpass

# 📌 Ansible Playbook 실행 (패스워드 자동 적용)
echo "🚀 Running Ansible Playbook: $PLAYBOOK_PATH"
echo "$PASSWARD" | ansible-playbook "$PLAYBOOK_PATH" --extra-vars "target_host=$TARGET_HOST ansible_become_pass=$PASSWARD"
echo "✅ Setup completed successfully!"

# 📌 Kubernetes 설정
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config

# 📌 Docker 그룹 적용 (현재 사용자가 새 그룹 적용을 위해 로그아웃/로그인 필요 없이 적용)
sudo usermod -aG docker $(whoami)
sudo systemctl restart docker