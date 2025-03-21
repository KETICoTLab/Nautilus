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

if ! command -v python3 &> /dev/null; then
    echo "🚀 Python3 is not installed. Installing Python3..."
    sudo apt install -y python3 python3-pip
fi

if ! command -v pip3 &> /dev/null; then
    echo "🚀 pip3 is not installed. Installing pip3..."
    sudo apt install -y python3-pip
fi

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "🚀 Installing Python dependencies from requirements.txt..."
    pip3 install --upgrade pip
    pip3 install -r "$REQUIREMENTS_FILE"
    echo "✅ Python dependencies installed successfully!"
else
    echo "⚠️ requirements.txt not found. Skipping Python dependencies installation."
fi

echo "🚀 Installing sshpass"
sudo apt-get install -y sshpass

echo "🚀 Running Ansible Playbook: $PLAYBOOK_PATH"
echo "$PASSWARD" | ansible-playbook "$PLAYBOOK_PATH" --extra-vars "target_host=$TARGET_HOST ansible_become_pass=$PASSWARD"
echo "✅ Setup completed successfully!"

mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
export KUBECONFIG=$HOME/.kube/config

echo "🚀 Applying docker group permissions for current session..."
newgrp docker
sudo systemctl restart docker

# 📌 NOPASSWD 설정 추가
echo "🚀 Ensuring NOPASSWD is set for current user ($USER)"
NOPASSWD_FILE="/etc/sudoers.d/99-$USER-nopasswd"

if [ ! -f "$NOPASSWD_FILE" ]; then
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee "$NOPASSWD_FILE" > /dev/null
    sudo chmod 0440 "$NOPASSWD_FILE"
    echo "✅ NOPASSWD 설정이 적용되었습니다: $NOPASSWD_FILE"
else
    echo "ℹ️ 이미 NOPASSWD 설정 파일이 존재합니다: $NOPASSWD_FILE"
fi
