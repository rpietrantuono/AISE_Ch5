
# Kubeflow Example

This example demonstrates how to install, configure, and use Kubeflow. Specifically, we'll create a basic pipeline to train a k-nearest neighbours classifier on the Iris dataset.

Since Kubeflow is built on Kubernetes, you'll need to have a local Kubernetes distribution running before you begin.

## Install Kind and Kubectl

Kind is a tool for creating local Kubernetes clusters using Docker containers as nodes. You can manage these clusters using the Kubernetes command-line tool, kubectl.

### For Linux
```
  # For AMD64 / x86_64
  [ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-amd64
  # For ARM64
  [ $(uname -m) = aarch64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-linux-arm64

  #Run these for both architectures
  chmod +x ./kind
  sudo mv ./kind /usr/local/bin/kind


  # For x86_64
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  # For ARM64
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/arm64/kubectl"

  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### macOS

```
  # For Intel
  [ $(uname -m) = x86_64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-darwin-amd64
  # For M1 / ARM
  [ $(uname -m) = arm64 ] && curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.24.0/kind-darwin-arm64
  
  #Run these for both architectures
  chmod +x ./kind
  mv ./kind /usr/local/bin/kind


  # For Intel
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
  # For M1 / ARM
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/arm64/kubectl"

  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
  sudo chown root: /usr/local/bin/kubectl
```

### Windows (on Powershell)
```
  curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.24.0/kind-windows-amd64
  Move-Item .\kind-windows-amd64.exe c:\some-dir-in-your-PATH\kind.exe
```
Install kubectl downloading it from https://kubernetes.io/releases/download/#binaries

## Set up a local Kubernetes cluster using Kind
 
```
cristian-msi@cristian-msi-Vector-GP68HX-13VH:~/Documents$ kind create cluster --name=aise
Creating cluster "aise" ...
 ✓ Ensuring node image (kindest/node:v1.31.0) 🖼
 ✓ Preparing nodes 📦  
 ✓ Writing configuration 📜 
 ✓ Starting control-plane 🕹️ 
 ✓ Installing CNI 🔌 
 ✓ Installing StorageClass 💾 
Set kubectl context to "kind-aise"
You can now use your cluster with:

kubectl cluster-info --context kind-aise

Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂

```

## Deploy kubeflow

Kubeflow can be deployed in various ways, including as standalone components or using the Kubeflow Platform. You can choose from package distributions or Kubeflow manifests. 
We'll deploy Kubeflow as a standalone component using manifests.

```
  kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=2.2.0"
  kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
  kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=2.2.0"
```
> 📝 The latest version (2.3.0) has issues with accessing the dashboard.

```
  cristian-msi@cristian-msi-Vector-GP68HX-13VH:~/Documents$ kubectl get pods -n kubeflow
  NAME                                               READY   STATUS             RESTARTS        AGE
  cache-deployer-deployment-f7dfbb98c-mj4j6          1/1     Running            0               14m
  cache-server-7676b74c4c-286jb                      1/1     Running            0               14m
  controller-manager-57488687d6-m6ssg                1/1     Running            0               14m
  metadata-envoy-deployment-5777f787c8-crx6h         1/1     Running            0               14m
  metadata-grpc-deployment-8496ffb98b-492dl          1/1     Running            7 (7m8s ago)    14m
  metadata-writer-c7f54cd7-gmzq6                     1/1     Running            3 (2m50s ago)   14m
  minio-7c77bc59b8-ld6gp                             1/1     Running            0               14m
  ml-pipeline-8fccd68b7-6fbvd                        1/1     Running            4 (5m46s ago)   14m
  ml-pipeline-persistenceagent-6b9c4b7f88-6rxkb      1/1     Running            2 (6m28s ago)   14m
  ml-pipeline-scheduledworkflow-7bdcd4c444-vr552     1/1     Running            0               14m
  ml-pipeline-ui-7975cb7c84-2lkxd                    1/1     Running            0               14m
  ml-pipeline-viewer-crd-868489f5f5-knqsj            1/1     Running            0               14m
  ml-pipeline-visualizationserver-549b97f7c7-l984j   1/1     Running            0               14m
  mysql-758cd66576-89dzw                             1/1     Running            0               14m
  proxy-agent-694b64d5f4-zkrmg                       0/1     CrashLoopBackOff   6 (37s ago)     14m
  workflow-controller-8679c8d76d-2hj22               1/1     Running            0               14m
```

> 📝 proxy-agent enters in CrashLoopBackOff, it will not be used. 

To access the dashboard, we must connect to the ml-pipeline-ui service. Since the cluster's services are not externally accessible, we'll need to set up port forwarding

```
  cristian-msi@cristian-msi-Vector-GP68HX-13VH:~/Documents$ kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
  Forwarding from 127.0.0.1:8080 -> 3000
  Forwarding from [::1]:8080 -> 3000  
```
Now, the dashboard is accessible from http://localhost:8080/pipeline/#
> 📝 The Kubeflow Pipelines REST API is available under the /pipeline/ HTTP path

## Run the pipeline

```
 cristian-msi@cristian-msi-Vector-GP68HX-13VH:~/Documents/AISE_Ch5$ python exmple_pipeline.py
  /home/cristian-msi/anaconda3/envs/test_kubeflow/lib/python3.10/site-packages/kfp/dsl/component_decorator.py:121: FutureWarning: The default base_image used by the @dsl.component decorator will switch from 'python:3.8' to 'python:3.9' on Oct 1, 2024. To ensure your existing components work with versions of the KFP SDK released after that date, you should provide an explicit base_image argument and ensure your component works as intended on Python 3.9.
  return component_factory.create_component_from_func(
/home/cristian-msi/anaconda3/envs/test_kubeflow/lib/python3.10/site-packages/kfp/client/client.py:159: FutureWarning: This client only works with Kubeflow Pipeline v2.0.0-beta.2 and later versions.
  warnings.warn(
Experiment details: /pipeline/#/experiments/details/356bae17-25bc-44ad-bc60-eb41c3a5fee9
Run details: /pipeline/#/runs/details/8543a968-6c6e-4716-bcb4-b12bde5041f5
localhost:8080/#/runs/details/8543a968-6c6e-4716-bcb4-b12bde5041f5
```

Some pods are created after the pipeline run and are marked as 'Completed' when they finish

```
  cristian-msi@cristian-msi-Vector-GP68HX-13VH:~/Documents$ kubectl get pods -n kubeflow
  NAME                                                              READY   STATUS             RESTARTS        AGE
  cache-deployer-deployment-f7dfbb98c-mj4j6                         1/1     Running            0               20m
  cache-server-7676b74c4c-286jb                                     1/1     Running            0               20m
  controller-manager-57488687d6-m6ssg                               1/1     Running            0               20m
  iris-training-pipeline-kc78z-system-container-driver-1793831555   0/2     Completed          0               68s
  iris-training-pipeline-kc78z-system-container-driver-851553022    0/2     Completed          0               2m56s
  iris-training-pipeline-kc78z-system-container-impl-1257429848     0/2     Completed          0               2m46s
  iris-training-pipeline-kc78z-system-container-impl-4043358533     0/2     Completed          0               58s
  iris-training-pipeline-kc78z-system-dag-driver-1046450884         0/2     Completed          0               8s
  iris-training-pipeline-kc78z-system-dag-driver-107824191          0/2     Completed          0               3m22s
  iris-training-pipeline-kc78z-system-dag-driver-2145114287         0/2     Completed          0               18s
  iris-training-pipeline-kc78z-system-dag-driver-3833327368         0/2     Completed          0               8s
  iris-training-pipeline-kc78z-system-dag-driver-972673396          0/2     Completed          0               8s
  metadata-envoy-deployment-5777f787c8-crx6h                        1/1     Running            0               20m
  metadata-grpc-deployment-8496ffb98b-492dl                         1/1     Running            7 (12m ago)     20m
  metadata-writer-c7f54cd7-gmzq6                                    1/1     Running            3 (8m11s ago)   20m
  minio-7c77bc59b8-ld6gp                                            1/1     Running            0               20m
  ml-pipeline-8fccd68b7-6fbvd                                       1/1     Running            4 (11m ago)     20m
  ml-pipeline-persistenceagent-6b9c4b7f88-6rxkb                     1/1     Running            2 (11m ago)     20m
  ml-pipeline-scheduledworkflow-7bdcd4c444-vr552                    1/1     Running            0               20m
  ml-pipeline-ui-7975cb7c84-2lkxd                                   1/1     Running            0               20m
  ml-pipeline-viewer-crd-868489f5f5-knqsj                           1/1     Running            0               20m
  ml-pipeline-visualizationserver-549b97f7c7-l984j                  1/1     Running            0               20m
  mysql-758cd66576-89dzw                                            1/1     Running            0               20m
  proxy-agent-694b64d5f4-zkrmg                                      0/1     CrashLoopBackOff   7 (56s ago)     20m
  workflow-controller-8679c8d76d-2hj22                              1/1     Running            0               20m
```

In the dashboard, we can see the pipeline

<img src="../img/pipeline_dashboard.png" alt="drawing" width="300"/>
