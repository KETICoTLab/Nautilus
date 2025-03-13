#!bin/bash

MY_IP=$(hostname -I | awk '{print $1}') 

KUBE_JOIN_COMMAND=$(cat ./kubeadm-join.sh)

ansible-playbook -i "$1," \
       --extra-vars "kube_join_command='$KUBE_JOIN_COMMAND'" \
       --extra-vars "minio_server_url=$MY_IP" \
       --vault-password-file ../../workspace/ansible_project/inventory/host_vars/vaultpass \
       --extra-vars "@../../workspace/ansible_project/inventory/host_vars/$1.yml" \
       --extra-vars "target_host=$1" \
       ./load_nautilus_img.yml