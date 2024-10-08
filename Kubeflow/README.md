## Instal Kind a toll for faciliting building and runnig of local kubernetes cluster


# For AMD64 / x86_64
[ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64

chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind


snap install kubectl

