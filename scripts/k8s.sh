#!/bin/bash

containerd_config_path="./config.toml"
kubeadm_config_path="./kubeadm-config.yaml"
# pod_network_addon_config_path="./pod-network-flannel.yml"
nginx_values_path="./nginx-values.yaml"


# BOOTSTRAP THE K8S CLUSTER FOR THE FIRST TIME
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf > /dev/null
br_netfilter
EOF
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf > /dev/null
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sudo sysctl --system

sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf > /dev/null
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf > /dev/null
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sudo sysctl --system

sudo mkdir -p /etc/containerd
# containerd config default | sudo tee /etc/containerd/config.toml
sudo cp ${containerd_config_path} /etc/containerd/
sudo systemctl restart containerd

sudo mkdir /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json > /dev/null
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF
sudo systemctl enable docker
sudo systemctl daemon-reload
sudo systemctl restart docker


# TO CLEAN UP THE K8S CLUSTER
# node_name=$(hostname)
# kubectl drain ${node_name} --delete-local-data --force --ignore-daemonsets
# kubectl delete node ${node_name}
# sudo kubeadm reset -f
# sudo rm -rf /etc/cni/net.d


# INITIALIZE THE K8S CLUSTER AND CONFIGURE kubectl
sudo kubeadm init --config ${kubeadm_config_path} --ignore-preflight-errors NumCPU
# sudo kubeadm init --pod-network-cidr=192.168.0.0/16 --ignore-preflight-errors NumCPU
mkdir -p $HOME/.kube
sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -un):$(id -gn) $HOME/.kube/config


# ALLOW PODS TO BE SCHEDULED ON MASTER AND INSTALL POD NETWORK ADD-ON
kubectl taint nodes --all node-role.kubernetes.io/master-
kubectl create -f https://docs.projectcalico.org/manifests/tigera-operator.yaml
# Note: Before creating this manifest, read its contents and make sure its settings
# are correct for your environment. For example, you may need to change the default
# IP pool CIDR to match your pod network CIDR.
kubectl create -f https://docs.projectcalico.org/manifests/custom-resources.yaml
# kubectl patch node $(hostname) -p '{"spec":{"podCIDR":"10.100.0.1/24"}}'
# kubectl apply -f ${pod_network_addon_config_path}
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-controller ingress-nginx/ingress-nginx --values ${nginx_values_path}
