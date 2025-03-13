#!bin/bash

MY_IP=$(hostname -I | awk '{print $1}') 

KUBE_JOIN_COMMAND=$(cat ./nautilus/nautilus/core/communicate/kubeadm-join.sh)

ansible-playbook -i "$1," \
       --extra-vars "kube_join_command='$KUBE_JOIN_COMMAND'" \
       --extra-vars "minio_server_url=$MY_IP" \
       --vault-password-file ./nautilus/workspace/ansible_project/inventory/host_vars/vaultpass \
       --extra-vars "@./nautilus/workspace/ansible_project/inventory/host_vars/$1.yml" \
       --extra-vars "target_host=$1" \
       ./nautilus/nautilus/core/communicate/load_nautilus_img.yml