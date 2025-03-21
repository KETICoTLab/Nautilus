#!/bin/bash

MY_IP=$(hostname -I | awk '{print $1}') 

# ✅ `kubeadm-join.sh`의 절대 경로 설정
SCRIPT_DIR=$(dirname "$(realpath "$0")")
KUBE_JOIN_COMMAND=$(cat "$SCRIPT_DIR/kubeadm-join.sh")

ansible-playbook -i "$1," \
       --extra-vars "kube_join_command='$KUBE_JOIN_COMMAND --node-name $2'" \
       --extra-vars "minio_server_url=$MY_IP" \
       --vault-password-file "$SCRIPT_DIR/../ansible_project/inventory/host_vars/vaultpass" \
       --extra-vars "@$SCRIPT_DIR/../ansible_project/inventory/host_vars/$1.yml" \
       --extra-vars "target_host=$1" \
       --extra-vars "node_name=$2" \
       --extra-vars "master_node_ip=$3" \
       "$SCRIPT_DIR/../ansible_project/playbook/load_client_join.yml"
